"""Tests for feature extraction functionality."""

import pytest
import numpy as np
from PIL import Image
import io

from ..pipeline.features import (
    extract_features, 
    preprocess_image, 
    extract_edge_features,
    extract_color_features,
    extract_compression_features,
    extract_noise_texture_features,
    compute_features_hash
)


def create_test_image(width=100, height=100, color=(128, 128, 128)):
    """Create a test image for testing."""
    img = Image.new('RGB', (width, height), color=color)
    return img


def image_to_bytes(img):
    """Convert PIL image to bytes."""
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()


def test_preprocess_image():
    """Test image preprocessing."""
    # Create test image
    img = create_test_image(200, 150)
    img_bytes = image_to_bytes(img)
    
    # Test preprocessing
    processed_img, metadata = preprocess_image(img_bytes)
    
    # Check output
    assert isinstance(processed_img, np.ndarray)
    assert len(processed_img.shape) == 3
    assert processed_img.shape[2] == 3  # RGB channels
    assert processed_img.dtype == np.uint8
    
    # Check metadata
    assert 'original_size' in metadata
    assert 'processed_size' in metadata
    assert 'channels' in metadata
    assert metadata['channels'] == 3


def test_preprocess_image_resize():
    """Test image resizing during preprocessing."""
    # Create large test image
    img = create_test_image(2000, 1500)
    img_bytes = image_to_bytes(img)
    
    # Test preprocessing with max_size
    processed_img, metadata = preprocess_image(img_bytes, max_size=500)
    
    # Should be resized
    assert max(processed_img.shape[:2]) <= 500
    assert metadata['resized'] is True


def test_extract_edge_features():
    """Test edge feature extraction."""
    # Create test image
    img = create_test_image(100, 100)
    img_array = np.array(img)
    
    # Extract features
    features = extract_edge_features(img_array)
    
    # Check output
    assert isinstance(features, np.ndarray)
    assert features.dtype == np.float32
    assert len(features) == 4  # edge_density, laplacian_var, grad_mean, grad_std
    assert np.all(np.isfinite(features))  # No NaN or inf values


def test_extract_color_features():
    """Test color feature extraction."""
    # Create colorful test image
    img = create_test_image(100, 100, color=(200, 100, 50))
    img_array = np.array(img)
    
    # Extract features
    features = extract_color_features(img_array)
    
    # Check output
    assert isinstance(features, np.ndarray)
    assert features.dtype == np.float32
    assert len(features) == 13  # RGB moments + HSV stats + entropy
    assert np.all(np.isfinite(features))


def test_extract_compression_features():
    """Test compression feature extraction."""
    # Create test image
    img = create_test_image(100, 100)
    img_array = np.array(img)
    
    # Extract features
    features = extract_compression_features(img_array)
    
    # Check output
    assert isinstance(features, np.ndarray)
    assert features.dtype == np.float32
    assert len(features) == 6  # DCT and variance features
    assert np.all(np.isfinite(features))


def test_extract_noise_texture_features():
    """Test noise and texture feature extraction."""
    # Create test image
    img = create_test_image(100, 100)
    img_array = np.array(img)
    
    # Extract features
    features = extract_noise_texture_features(img_array)
    
    # Check output
    assert isinstance(features, np.ndarray)
    assert features.dtype == np.float32
    assert len(features) == 8  # Noise and texture features
    assert np.all(np.isfinite(features))


def test_extract_features_complete():
    """Test complete feature extraction."""
    # Create test image
    img = create_test_image(100, 100)
    img_array = np.array(img)
    
    # Extract complete feature vector
    features = extract_features(img_array)
    
    # Check output
    assert isinstance(features, np.ndarray)
    assert features.dtype == np.float32
    assert len(features) == 30  # Total expected features
    assert np.all(np.isfinite(features))


def test_extract_features_deterministic():
    """Test that feature extraction is deterministic."""
    # Create test image
    img = create_test_image(100, 100, color=(123, 45, 67))
    img_array = np.array(img)
    
    # Extract features twice
    features1 = extract_features(img_array)
    features2 = extract_features(img_array)
    
    # Should be identical
    np.testing.assert_array_equal(features1, features2)


def test_extract_features_different_images():
    """Test that different images produce different features."""
    # Create two different test images
    img1 = create_test_image(100, 100, color=(255, 0, 0))  # Red
    img2 = create_test_image(100, 100, color=(0, 255, 0))  # Green
    
    img1_array = np.array(img1)
    img2_array = np.array(img2)
    
    # Extract features
    features1 = extract_features(img1_array)
    features2 = extract_features(img2_array)
    
    # Should be different
    assert not np.array_equal(features1, features2)


def test_compute_features_hash():
    """Test feature hash computation."""
    # Create test features
    features = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32)
    
    # Compute hash
    hash1 = compute_features_hash(features)
    hash2 = compute_features_hash(features)
    
    # Should be consistent
    assert hash1 == hash2
    assert isinstance(hash1, str)
    assert len(hash1) == 32  # MD5 hash length


def test_features_with_invalid_input():
    """Test feature extraction with edge cases."""
    # Test with very small image
    small_img = create_test_image(10, 10)
    small_array = np.array(small_img)
    
    features = extract_features(small_array)
    assert len(features) == 30
    assert np.all(np.isfinite(features))
    
    # Test with single color image
    uniform_img = create_test_image(50, 50, color=(128, 128, 128))
    uniform_array = np.array(uniform_img)
    
    features = extract_features(uniform_array)
    assert len(features) == 30
    assert np.all(np.isfinite(features))