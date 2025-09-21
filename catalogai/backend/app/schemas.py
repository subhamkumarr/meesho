"""Pydantic schemas for API request/response validation."""

from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import List, Optional


class ScanResult(BaseModel):
    """Schema for individual scan result."""
    
    filename: str
    size: int
    mime_type: str
    score: float = Field(ge=0.0, le=1.0, description="Synthetic probability score")
    label: str = Field(description="Classification: authentic/suspicious/synthetic")
    reasons: List[str] = Field(description="List of reasoning explanations")
    processing_time_ms: Optional[float] = Field(description="Processing time in milliseconds")


class ScanResponse(BaseModel):
    """Schema for scan endpoint response."""
    
    results: List[ScanResult]
    total_processed: int
    total_time_ms: float


class ScanOut(BaseModel):
    """Schema for scan database record output."""
    
    id: int
    filename: str
    size: int
    mime_type: str
    score: float
    label: str
    reasons: List[str]
    features_hash: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ScanListResponse(BaseModel):
    """Schema for paginated scan list response."""
    
    scans: List[ScanOut]
    total: int
    page: int
    per_page: int
    has_next: bool


class ThresholdsIn(BaseModel):
    """Schema for threshold update request."""
    
    thresh_auth: float = Field(ge=0.0, le=1.0, description="Threshold for authentic classification")
    thresh_syn: float = Field(ge=0.0, le=1.0, description="Threshold for synthetic classification")
    
    @validator('thresh_syn')
    def validate_threshold_order(cls, v, values):
        if 'thresh_auth' in values and v <= values['thresh_auth']:
            raise ValueError('thresh_syn must be greater than thresh_auth')
        return v


class ThresholdsOut(BaseModel):
    """Schema for threshold configuration response."""
    
    thresh_auth: float
    thresh_syn: float
    updated_at: datetime
    updated_by: str


class TrainingResponse(BaseModel):
    """Schema for model training response."""
    
    success: bool
    message: str
    metrics: dict
    training_time_ms: float


class HealthResponse(BaseModel):
    """Schema for health check response."""
    
    status: str
    timestamp: datetime
    model_loaded: bool
    database_connected: bool
    version: str = "1.0.0"


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)