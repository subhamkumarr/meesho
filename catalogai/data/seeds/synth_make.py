"""Generate synthetic-looking images for training data."""

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import random
import math
from typing import List


def create_gradient_background(width: int, height: int, colors: List[tuple]) -> Image.Image:
    """Create a smooth gradient background."""
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)
    
    # Create linear gradient
    for y in range(height):
        ratio = y / height
        
        # Interpolate between colors
        if len(colors) >= 2:
            r = int(colors[0][0] * (1 - ratio) + colors[1][0] * ratio)
            g = int(colors[0][1] * (1 - ratio) + colors[1][1] * ratio)
            b = int(colors[0][2] * (1 - ratio) + colors[1][2] * ratio)
        else:
            r, g, b = colors[0]
        
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    return img


def create_geometric_pattern(width: int, height: int) -> Image.Image:
    """Create geometric patterns typical of AI-generated images."""
    img = Image.new('RGB', (width, height), color=(240, 240, 240))
    draw = ImageDraw.Draw(img)
    
    # Random geometric shapes with perfect symmetry
    center_x, center_y = width // 2, height // 2
    
    # Create concentric circles or polygons
    pattern_type = random.choice(['circles', 'polygons', 'lines'])
    
    if pattern_type == 'circles':
        for i in range(5, min(width, height) // 2, 20):
            color = (
                random.randint(100, 255),
                random.randint(100, 255),
                random.randint(100, 255)
            )
            draw.ellipse([
                center_x - i, center_y - i,
                center_x + i, center_y + i
            ], outline=color, width=2)
    
    elif pattern_type == 'polygons':
        sides = random.choice([6, 8, 12])
        for radius in range(20, min(width, height) // 2, 30):
            points = []
            for i in range(sides):
                angle = 2 * math.pi * i / sides
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                points.append((x, y))
            
            color = (
                random.randint(100, 255),
                random.randint(100, 255),
                random.randint(100, 255)
            )
            draw.polygon(points, outline=color, width=2)
    
    else:  # lines
        for i in range(0, width, 20):
            color = (
                random.randint(100, 255),
                random.randint(100, 255),
                random.randint(100, 255)
            )
            draw.line([(i, 0), (i, height)], fill=color, width=2)
        
        for i in range(0, height, 20):
            color = (
                random.randint(100, 255),
                random.randint(100, 255),
                random.randint(100, 255)
            )
            draw.line([(0, i), (width, i)], fill=color, width=2)
    
    return img


def create_smooth_blob(width: int, height: int) -> Image.Image:
    """Create smooth, over-processed looking shapes."""
    img = Image.new('RGB', (width, height), color=(200, 200, 200))
    draw = ImageDraw.Draw(img)
    
    # Create random smooth blobs
    for _ in range(random.randint(3, 8)):
        # Random blob position and size
        x = random.randint(width // 4, 3 * width // 4)
        y = random.randint(height // 4, 3 * height // 4)
        size = random.randint(30, min(width, height) // 3)
        
        # Bright, saturated colors
        color = (
            random.randint(150, 255),
            random.randint(150, 255),
            random.randint(150, 255)
        )
        
        # Draw ellipse
        draw.ellipse([
            x - size, y - size,
            x + size, y + size
        ], fill=color)
    
    # Apply heavy blur to make it look over-processed
    img = img.filter(ImageFilter.GaussianBlur(radius=8))
    
    return img


def create_artificial_texture(width: int, height: int) -> Image.Image:
    """Create artificial-looking textures with repetitive patterns."""
    img = Image.new('RGB', (width, height))
    pixels = img.load()
    
    # Create repetitive noise pattern
    pattern_size = 16
    base_pattern = np.random.randint(0, 256, (pattern_size, pattern_size, 3))
    
    for y in range(height):
        for x in range(width):
            # Tile the pattern
            px = x % pattern_size
            py = y % pattern_size
            
            # Add some variation but keep it artificial
            r, g, b = base_pattern[py, px]
            
            # Add slight variation
            r = max(0, min(255, r + random.randint(-10, 10)))
            g = max(0, min(255, g + random.randint(-10, 10)))
            b = max(0, min(255, b + random.randint(-10, 10)))
            
            pixels[x, y] = (r, g, b)
    
    return img


def create_uniform_lighting(width: int, height: int) -> Image.Image:
    """Create image with unnaturally uniform lighting."""
    # Start with gradient
    colors = [
        (random.randint(180, 255), random.randint(180, 255), random.randint(180, 255)),
        (random.randint(180, 255), random.randint(180, 255), random.randint(180, 255))
    ]
    img = create_gradient_background(width, height, colors)
    
    # Add some simple shapes with uniform lighting
    draw = ImageDraw.Draw(img)
    
    # Add rectangles with perfect uniform colors
    for _ in range(random.randint(2, 5)):
        x1 = random.randint(0, width // 2)
        y1 = random.randint(0, height // 2)
        x2 = x1 + random.randint(50, width // 3)
        y2 = y1 + random.randint(50, height // 3)
        
        color = (
            random.randint(100, 255),
            random.randint(100, 255),
            random.randint(100, 255)
        )
        
        draw.rectangle([x1, y1, x2, y2], fill=color)
    
    # Apply slight blur to reduce any natural-looking edges
    img = img.filter(ImageFilter.GaussianBlur(radius=2))
    
    return img


def generate_synthetic_images(count: int) -> List[np.ndarray]:
    """
    Generate synthetic-looking images for training.
    
    Args:
        count: Number of images to generate
        
    Returns:
        List of image arrays
    """
    images = []
    
    generators = [
        create_gradient_background,
        create_geometric_pattern,
        create_smooth_blob,
        create_artificial_texture,
        create_uniform_lighting
    ]
    
    for i in range(count):
        # Random image size
        width = random.randint(200, 400)
        height = random.randint(200, 400)
        
        # Choose random generator
        if i < len(generators):
            # Ensure we use each generator at least once
            generator = generators[i % len(generators)]
        else:
            generator = random.choice(generators)
        
        try:
            if generator == create_gradient_background:
                colors = [
                    (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)),
                    (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
                ]
                img = generator(width, height, colors)
            else:
                img = generator(width, height)
            
            # Convert to numpy array
            img_array = np.array(img)
            images.append(img_array)
            
        except Exception as e:
            print(f"Error generating synthetic image {i}: {e}")
            # Create fallback simple image
            fallback = Image.new('RGB', (width, height), color=(200, 200, 200))
            images.append(np.array(fallback))
    
    print(f"Generated {len(images)} synthetic images")
    return images


if __name__ == "__main__":
    # Test generation
    test_images = generate_synthetic_images(5)
    print(f"Test generated {len(test_images)} images")
    for i, img in enumerate(test_images):
        print(f"Image {i}: shape {img.shape}, dtype {img.dtype}")