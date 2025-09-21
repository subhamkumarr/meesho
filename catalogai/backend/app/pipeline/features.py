"""Feature extraction for image authenticity detection."""

import cv2
import numpy as np
from PIL import Image
from scipy import ndimage
from scipy.fft import fft2, fftshift
from scipy.stats import skew, kurtosis
import logging
from typing import Tuple, Optional
import hashlib

logger = logging.getLogger(__name__)


def preprocess_image(image_bytes: bytes, max_size: int = 1024) -> Tuple[np.ndarray, dict]:
    """
    Preprocess image for feature extraction.
    
    Args:
        image_bytes: Raw image bytes
        max_size: Maximum dimension size for resizing
        
    Returns:
        Tuple of (processed_image_array, metadata)
    """
    try:
        # Load image with PIL
        pil_image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if needed
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # Get original dimensions
        orig_width, orig_height = pil_image.size
        
        # Resize if too large
        if max(orig_width, orig_height) > max_size:
            ratio = max_size / max(orig_width, orig_height)
            new_width = int(orig_width * ratio)
            new_height = int(orig_height * ratio)
            pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Convert to numpy array
        img_array = np.array(pil_image)
        
        metadata = {
            'original_size': (orig_width, orig_height),
            'processed_size': img_array.shape[:2],
            'channels': img_array.shape[2] if len(img_array.shape) > 2 else 1,
            'resized': max(orig_width, orig_height) > max_size
        }
        
        return img_array, metadata
        
    except Exception as e:
        logger.error(f"Error preprocessing image: {e}")
        raise ValueError(f"Invalid image format or corrupted data: {e}")


def extract_edge_features(img: np.ndarray) -> np.ndarray:
    """Extract edge-based features."""
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
    # Canny edge detection
    edges = cv2.Canny(gray, 50, 150)
    edge_density = np.sum(edges > 0) / edges.size
    
    # Laplacian variance (sharpness measure)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    laplacian_var = np.var(laplacian)
    
    # Gradient magnitude statistics
    grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    grad_mag = np.sqrt(grad_x**2 + grad_y**2)
    
    grad_mean = np.mean(grad_mag)
    grad_std = np.std(grad_mag)
    
    return np.array([edge_density, laplacian_var, grad_mean, grad_std], dtype=np.float32)


def extract_color_features(img: np.ndarray) -> np.ndarray:
    """Extract color-based features."""
    features = []
    
    # RGB histogram moments
    for channel in range(3):
        channel_data = img[:, :, channel].flatten()
        
        # Basic statistics
        mean_val = np.mean(channel_data)
        std_val = np.std(channel_data)
        skew_val = skew(channel_data)
        
        features.extend([mean_val, std_val, skew_val])
    
    # Convert to HSV for additional features
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    
    # Saturation statistics
    sat_channel = hsv[:, :, 1].flatten()
    sat_mean = np.mean(sat_channel)
    sat_std = np.std(sat_channel)
    
    # Value (brightness) statistics
    val_channel = hsv[:, :, 2].flatten()
    val_mean = np.mean(val_channel)
    val_std = np.std(val_channel)
    
    # Color entropy
    hist, _ = np.histogram(img.flatten(), bins=256, range=(0, 256))
    hist = hist / np.sum(hist)  # Normalize
    entropy = -np.sum(hist * np.log2(hist + 1e-10))
    
    features.extend([sat_mean, sat_std, val_mean, val_std, entropy])
    
    return np.array(features, dtype=np.float32)


def extract_compression_features(img: np.ndarray) -> np.ndarray:
    """Extract compression artifact features."""
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
    # DCT-based features (JPEG compression proxy)
    # Divide image into 8x8 blocks and analyze DCT coefficients
    h, w = gray.shape
    block_size = 8
    
    dct_features = []
    
    for i in range(0, h - block_size + 1, block_size):
        for j in range(0, w - block_size + 1, block_size):
            block = gray[i:i+block_size, j:j+block_size].astype(np.float32)
            
            # Apply DCT
            dct_block = cv2.dct(block)
            
            # Extract features from DCT coefficients
            # High frequency energy (compression artifacts)
            high_freq = dct_block[4:, 4:]
            high_freq_energy = np.sum(high_freq**2)
            
            dct_features.append(high_freq_energy)
    
    if dct_features:
        dct_mean = np.mean(dct_features)
        dct_std = np.std(dct_features)
        dct_max = np.max(dct_features)
    else:
        dct_mean = dct_std = dct_max = 0.0
    
    # Block artifact detection using local variance
    block_vars = []
    for i in range(0, h - block_size + 1, block_size//2):
        for j in range(0, w - block_size + 1, block_size//2):
            block = gray[i:i+block_size, j:j+block_size]
            block_vars.append(np.var(block))
    
    if block_vars:
        var_mean = np.mean(block_vars)
        var_std = np.std(block_vars)
        var_ratio = var_std / (var_mean + 1e-10)
    else:
        var_mean = var_std = var_ratio = 0.0
    
    return np.array([dct_mean, dct_std, dct_max, var_mean, var_std, var_ratio], dtype=np.float32)


def extract_noise_texture_features(img: np.ndarray) -> np.ndarray:
    """Extract noise and texture features."""
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY).astype(np.float32)
    
    # Noise estimation using bilateral filter residual
    bilateral = cv2.bilateralFilter(gray.astype(np.uint8), 9, 75, 75).astype(np.float32)
    noise_residual = gray - bilateral
    noise_energy = np.var(noise_residual)
    noise_mean = np.mean(np.abs(noise_residual))
    
    # Texture analysis using local binary patterns approximation
    # Simple texture measure using local variance
    kernel = np.ones((3, 3), np.float32) / 9
    local_mean = cv2.filter2D(gray, -1, kernel)
    local_var = cv2.filter2D(gray**2, -1, kernel) - local_mean**2
    
    texture_mean = np.mean(local_var)
    texture_std = np.std(local_var)
    
    # FFT-based periodicity detection
    f_transform = fft2(gray)
    f_shift = fftshift(f_transform)
    magnitude_spectrum = np.abs(f_shift)
    
    # Radial frequency analysis
    h, w = magnitude_spectrum.shape
    center_y, center_x = h // 2, w // 2
    
    # Create radial frequency bins
    y, x = np.ogrid[:h, :w]
    r = np.sqrt((x - center_x)**2 + (y - center_y)**2)
    
    # Analyze energy in different frequency rings
    ring1 = np.mean(magnitude_spectrum[(r >= 10) & (r < 20)])
    ring2 = np.mean(magnitude_spectrum[(r >= 20) & (r < 40)])
    ring3 = np.mean(magnitude_spectrum[(r >= 40) & (r < 80)])
    
    # Periodicity measure
    periodicity = ring2 / (ring1 + ring3 + 1e-10)
    
    return np.array([noise_energy, noise_mean, texture_mean, texture_std, 
                    ring1, ring2, ring3, periodicity], dtype=np.float32)


def extract_features(img: np.ndarray) -> np.ndarray:
    """
    Extract complete feature vector from image.
    
    Args:
        img: RGB image array
        
    Returns:
        Feature vector as 1D numpy array
    """
    try:
        # Extract different feature groups
        edge_features = extract_edge_features(img)
        color_features = extract_color_features(img)
        compression_features = extract_compression_features(img)
        noise_texture_features = extract_noise_texture_features(img)
        
        # Combine all features
        feature_vector = np.concatenate([
            edge_features,
            color_features,
            compression_features,
            noise_texture_features
        ])
        
        # Ensure no NaN or infinite values
        feature_vector = np.nan_to_num(feature_vector, nan=0.0, posinf=1e6, neginf=-1e6)
        
        return feature_vector.astype(np.float32)
        
    except Exception as e:
        logger.error(f"Error extracting features: {e}")
        # Return zero vector as fallback
        return np.zeros(30, dtype=np.float32)


def compute_features_hash(features: np.ndarray) -> str:
    """Compute hash of feature vector for reproducibility tracking."""
    feature_bytes = features.tobytes()
    return hashlib.md5(feature_bytes).hexdigest()


# Import io module that was missing
import io