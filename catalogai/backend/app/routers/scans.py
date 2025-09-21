"""Image scanning endpoints for CatalogAI."""

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlmodel import Session, select
from typing import List
import time
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
import hashlib

from ..schemas import ScanResponse, ScanResult, ScanOut, ScanListResponse
from ..models import Scan
from ..db import get_session
from ..config import settings
from ..pipeline.classifier import predict
from ..pipeline.features import compute_features_hash, extract_features, preprocess_image

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/scans", tags=["scans"])

# Thread pool for parallel processing
executor = ThreadPoolExecutor(max_workers=4)


def validate_upload_file(file: UploadFile) -> None:
    """Validate uploaded file."""
    # Check file size
    if hasattr(file, 'size') and file.size:
        if file.size > settings.max_image_mb * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {settings.max_image_mb}MB"
            )
    
    # Check MIME type
    if file.content_type and not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400,
            detail="File must be an image"
        )


async def process_single_image(file: UploadFile) -> ScanResult:
    """Process a single image file."""
    start_time = time.time()
    
    try:
        # Validate file
        validate_upload_file(file)
        
        # Read file content
        content = await file.read()
        
        # Validate content size
        if len(content) > settings.max_image_mb * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {settings.max_image_mb}MB"
            )
        
        # Run prediction in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        score, label, reasons = await loop.run_in_executor(
            executor, predict, content
        )
        
        processing_time = (time.time() - start_time) * 1000
        
        return ScanResult(
            filename=file.filename or "unknown",
            size=len(content),
            mime_type=file.content_type or "application/octet-stream",
            score=score,
            label=label,
            reasons=reasons,
            processing_time_ms=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing image {file.filename}: {e}")
        processing_time = (time.time() - start_time) * 1000
        
        return ScanResult(
            filename=file.filename or "unknown",
            size=0,
            mime_type=file.content_type or "application/octet-stream",
            score=0.5,
            label="error",
            reasons=[f"Processing error: {str(e)}"],
            processing_time_ms=processing_time
        )


def save_scan_result(session: Session, result: ScanResult) -> None:
    """Save scan result to database."""
    try:
        # Compute features hash for reproducibility
        # This is a simplified version - in practice we'd store the actual features
        content_hash = hashlib.md5(f"{result.filename}{result.size}".encode()).hexdigest()
        
        scan = Scan(
            filename=result.filename,
            size=result.size,
            mime_type=result.mime_type,
            score=result.score,
            label=result.label,
            reasons="",  # Will be set by set_reasons_list
            features_hash=content_hash
        )
        
        scan.set_reasons_list(result.reasons)
        
        session.add(scan)
        session.commit()
        
    except Exception as e:
        logger.error(f"Error saving scan result: {e}")
        session.rollback()


@router.post("/", response_model=ScanResponse)
async def scan_images(
    files: List[UploadFile] = File(...),
    session: Session = Depends(get_session)
):
    """
    Scan uploaded images for authenticity.
    
    Accepts multiple image files and returns authenticity analysis for each.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    if len(files) > 10:  # Reasonable limit
        raise HTTPException(status_code=400, detail="Too many files. Maximum 10 files per request")
    
    start_time = time.time()
    results = []
    
    try:
        # Process all files concurrently
        tasks = [process_single_image(file) for file in files]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions in results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error processing file {i}: {result}")
                processed_results.append(ScanResult(
                    filename=files[i].filename or f"file_{i}",
                    size=0,
                    mime_type="application/octet-stream",
                    score=0.5,
                    label="error",
                    reasons=[f"Processing failed: {str(result)}"],
                    processing_time_ms=0
                ))
            else:
                processed_results.append(result)
        
        # Save results to database
        for result in processed_results:
            if result.label != "error":  # Only save successful scans
                save_scan_result(session, result)
        
        total_time = (time.time() - start_time) * 1000
        
        return ScanResponse(
            results=processed_results,
            total_processed=len(processed_results),
            total_time_ms=total_time
        )
        
    except Exception as e:
        logger.error(f"Error in scan endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during scanning")


@router.get("/", response_model=ScanListResponse)
async def list_scans(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    session: Session = Depends(get_session)
):
    """
    List historical scan results with pagination.
    """
    try:
        # Calculate offset
        offset = (page - 1) * per_page
        
        # Get total count
        total_query = select(Scan)
        total_result = session.exec(total_query)
        total = len(list(total_result))
        
        # Get paginated results
        query = select(Scan).order_by(Scan.created_at.desc()).offset(offset).limit(per_page)
        scans = session.exec(query).all()
        
        # Convert to output format
        scan_outputs = []
        for scan in scans:
            scan_out = ScanOut(
                id=scan.id,
                filename=scan.filename,
                size=scan.size,
                mime_type=scan.mime_type,
                score=scan.score,
                label=scan.label,
                reasons=scan.get_reasons_list(),
                features_hash=scan.features_hash,
                created_at=scan.created_at
            )
            scan_outputs.append(scan_out)
        
        has_next = (page * per_page) < total
        
        return ScanListResponse(
            scans=scan_outputs,
            total=total,
            page=page,
            per_page=per_page,
            has_next=has_next
        )
        
    except Exception as e:
        logger.error(f"Error listing scans: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving scan history")