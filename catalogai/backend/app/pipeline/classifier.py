"""ML classifier for image authenticity detection."""

import joblib
import numpy as np
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.calibration import CalibratedClassifierCV
from pathlib import Path
from PIL import Image
import random
import logging
import json
import time
from typing import Tuple, Dict, Optional
import os

from .features import extract_features, preprocess_image, compute_features_hash
from .reasons import reasons_from_features
from ..config import settings

logger = logging.getLogger(__name__)

# Global model and scaler instances
_model = None
_scaler = None
_model_loaded = False

ARTIFACTS_DIR = Path(__file__).parent / "artifacts"


def ensure_artifacts_dir():
    """Ensure artifacts directory exists."""
    ARTIFACTS_DIR.mkdir(exist_ok=True)


def _load_real_images_from_dir(folder: Path, max_count: int = 2000) -> list:
    """Load up to max_count RGB images as numpy arrays from a directory tree."""
    try:
        if not folder.exists():
            return []
        # Collect files
        exts = ["*.jpg", "*.jpeg", "*.png", "*.bmp"]
        files = []
        for ext in exts:
            files.extend(folder.rglob(ext))
        if not files:
            return []
        # Sample deterministically for reproducibility
        random.seed(42)
        files = random.sample(files, k=min(max_count, len(files)))

        images: list[np.ndarray] = []
        for p in files:
            try:
                img = Image.open(p).convert('RGB')
                # Light downscale to control memory/time
                img.thumbnail((768, 768))
                images.append(np.array(img))
            except Exception:
                # Skip unreadable files
                continue
        return images
    except Exception:
        return []


def train(seed_dir: Path) -> Dict:
    """
    Train the authenticity detection model.
    
    Args:
        seed_dir: Directory containing seed data generation scripts
        
    Returns:
        Dictionary with training metrics
    """
    ensure_artifacts_dir()
    
    start_time = time.time()
    
    try:
        # Import seed data generators
        import sys
        sys.path.append(str(seed_dir))
        
        from synth_make import generate_synthetic_images
        from real_make import generate_realistic_images
        
        logger.info("Generating training data...")
        
        # Generate synthetic images (label = 1)
        synthetic_images = generate_synthetic_images(60)
        synthetic_labels = np.ones(len(synthetic_images))
        
        # Generate realistic images (label = 0)
        realistic_images = generate_realistic_images(60)
        # Optionally mix in real images from disk if available
        real_dir = Path(__file__).parent.parent.parent / "data" / "real"
        disk_real_images = _load_real_images_from_dir(real_dir, max_count=2000)
        if disk_real_images:
            realistic_images.extend(disk_real_images)
        realistic_labels = np.zeros(len(realistic_images))
        
        # Combine datasets
        all_images = synthetic_images + realistic_images
        all_labels = np.concatenate([synthetic_labels, realistic_labels])
        
        logger.info(f"Generated {len(all_images)} training images")
        if disk_real_images:
            logger.info(f"Mixed in {len(disk_real_images)} real images from {real_dir}")
        
        # Extract features
        logger.info("Extracting features...")
        features_list = []
        
        for i, img_array in enumerate(all_images):
            try:
                features = extract_features(img_array)
                features_list.append(features)
            except Exception as e:
                logger.warning(f"Failed to extract features from image {i}: {e}")
                # Use zero vector as fallback
                features_list.append(np.zeros(30, dtype=np.float32))
        
        X = np.array(features_list)
        y = all_labels
        
        logger.info(f"Feature matrix shape: {X.shape}")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train SVM with probability calibration
        logger.info("Training SVM classifier...")
        base_svm = SVC(
            kernel='rbf',
            class_weight='balanced',
            random_state=42,
            gamma='scale'
        )
        
        # Use calibrated classifier for probability estimates
        model = CalibratedClassifierCV(base_svm, method='sigmoid', cv=3)
        model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        y_pred = model.predict(X_test_scaled)
        y_proba = model.predict_proba(X_test_scaled)
        
        accuracy = accuracy_score(y_test, y_pred)
        
        # Create metrics dictionary
        metrics = {
            'accuracy': float(accuracy),
            'n_train_samples': len(X_train),
            'n_test_samples': len(X_test),
            'n_features': X.shape[1],
            'classification_report': classification_report(y_test, y_pred, output_dict=True),
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
            'training_time_seconds': time.time() - start_time,
            'disk_real_images_used': int(len(disk_real_images)) if 'disk_real_images' in locals() else 0
        }
        
        # Save model and scaler
        model_path = ARTIFACTS_DIR / "model.joblib"
        scaler_path = ARTIFACTS_DIR / "scaler.joblib"
        metrics_path = ARTIFACTS_DIR / "metrics.json"
        
        joblib.dump(model, model_path)
        joblib.dump(scaler, scaler_path)
        
        with open(metrics_path, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        logger.info(f"Model trained successfully. Accuracy: {accuracy:.3f}")
        logger.info(f"Model saved to {model_path}")
        
        # Update global model instances
        global _model, _scaler, _model_loaded
        _model = model
        _scaler = scaler
        _model_loaded = True
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error training model: {e}")
        raise


def load_model() -> Tuple[Optional[object], Optional[object]]:
    """Load trained model and scaler."""
    global _model, _scaler, _model_loaded
    
    if _model_loaded and _model is not None and _scaler is not None:
        return _model, _scaler
    
    try:
        model_path = ARTIFACTS_DIR / "model.joblib"
        scaler_path = ARTIFACTS_DIR / "scaler.joblib"
        
        if not model_path.exists() or not scaler_path.exists():
            logger.warning("Model artifacts not found. Need to train model first.")
            return None, None
        
        _model = joblib.load(model_path)
        _scaler = joblib.load(scaler_path)
        _model_loaded = True
        
        logger.info("Model loaded successfully")
        return _model, _scaler
        
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        return None, None


def predict(image_bytes: bytes) -> Tuple[float, str, list[str]]:
    """
    Predict authenticity of an image.
    
    Args:
        image_bytes: Raw image bytes
        
    Returns:
        Tuple of (synthetic_probability, label, reasons)
    """
    try:
        # Load model if not already loaded
        model, scaler = load_model()
        
        if model is None or scaler is None:
            raise ValueError("Model not available. Please train the model first.")
        
        # Preprocess image
        img_array, metadata = preprocess_image(image_bytes)
        
        # Extract features
        features = extract_features(img_array)
        features_scaled = scaler.transform(features.reshape(1, -1))
        
        # Get prediction probability
        proba = model.predict_proba(features_scaled)[0]
        synthetic_prob = proba[1]  # Probability of synthetic class
        
        # Map to label based on thresholds
        if synthetic_prob < settings.thresh_auth:
            label = "authentic"
        elif synthetic_prob < settings.thresh_syn:
            label = "suspicious"
        else:
            label = "synthetic"
        
        # Generate explanations
        reasons = reasons_from_features(features, {
            'synthetic_prob': synthetic_prob,
            'label': label,
            'metadata': metadata
        })
        
        return float(synthetic_prob), label, reasons
        
    except Exception as e:
        logger.error(f"Error in prediction: {e}")
        # Return fallback prediction
        return 0.5, "suspicious", [f"Error in analysis: {str(e)}"]


def is_model_available() -> bool:
    """Check if model is available for predictions."""
    model_path = ARTIFACTS_DIR / "model.joblib"
    scaler_path = ARTIFACTS_DIR / "scaler.joblib"
    return model_path.exists() and scaler_path.exists()


def get_model_metrics() -> Optional[Dict]:
    """Get saved model metrics."""
    try:
        metrics_path = ARTIFACTS_DIR / "metrics.json"
        if metrics_path.exists():
            with open(metrics_path, 'r') as f:
                return json.load(f)
        return None
    except Exception as e:
        logger.error(f"Error loading metrics: {e}")
        return None