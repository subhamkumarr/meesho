"""Orchestrate training data generation for CatalogAI."""

import sys
import os
from pathlib import Path
import numpy as np
import logging

# Add current directory to path for imports
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from synth_make import generate_synthetic_images
from real_make import generate_realistic_images

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_training_dataset(synthetic_count: int = 60, realistic_count: int = 60):
    """
    Generate complete training dataset.
    
    Args:
        synthetic_count: Number of synthetic images to generate
        realistic_count: Number of realistic images to generate
        
    Returns:
        Tuple of (images_list, labels_array)
    """
    logger.info("Starting training data generation...")
    
    # Generate synthetic images (label = 1)
    logger.info(f"Generating {synthetic_count} synthetic images...")
    synthetic_images = generate_synthetic_images(synthetic_count)
    synthetic_labels = np.ones(len(synthetic_images))
    
    # Generate realistic images (label = 0)
    logger.info(f"Generating {realistic_count} realistic images...")
    realistic_images = generate_realistic_images(realistic_count)
    realistic_labels = np.zeros(len(realistic_images))
    
    # Combine datasets
    all_images = synthetic_images + realistic_images
    all_labels = np.concatenate([synthetic_labels, realistic_labels])
    
    logger.info(f"Generated total of {len(all_images)} training images")
    logger.info(f"Synthetic: {len(synthetic_images)}, Realistic: {len(realistic_images)}")
    
    return all_images, all_labels


def validate_generated_data(images, labels):
    """Validate the generated training data."""
    logger.info("Validating generated data...")
    
    if len(images) != len(labels):
        raise ValueError(f"Mismatch: {len(images)} images vs {len(labels)} labels")
    
    # Check image properties
    for i, img in enumerate(images[:5]):  # Check first 5
        if not isinstance(img, np.ndarray):
            raise ValueError(f"Image {i} is not numpy array: {type(img)}")
        
        if len(img.shape) != 3 or img.shape[2] != 3:
            raise ValueError(f"Image {i} has wrong shape: {img.shape}")
        
        if img.dtype != np.uint8:
            logger.warning(f"Image {i} has dtype {img.dtype}, expected uint8")
    
    # Check label distribution
    unique_labels, counts = np.unique(labels, return_counts=True)
    logger.info(f"Label distribution: {dict(zip(unique_labels, counts))}")
    
    logger.info("Data validation passed")


if __name__ == "__main__":
    try:
        # Generate training data
        images, labels = generate_training_dataset()
        
        # Validate data
        validate_generated_data(images, labels)
        
        logger.info("Training data generation completed successfully")
        
    except Exception as e:
        logger.error(f"Error in training data generation: {e}")
        sys.exit(1)