"""Generate realistic-looking images for training data."""

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import random
import math
from typing import List, Tuple


def add_camera_noise(img: Image.Image, intensity: float = 0.1) -> Image.Image:
    """Add realistic camera noise to image."""
    img_array = np.array(img)
    
    # Add Gaussian noise
    noise = np.random.normal(0, intensity * 255, img_array.shape)
    noisy_array = img_array.astype(np.float32) + noise
    
    # Clip values
    noisy_array = np.clip(noisy_array, 0, 255).astype(np.uint8)
    
    return Image.fromarray(noisy_array)


def add_perspective_distortion(img: Image.Image) -> Image.Image:
    """Add slight perspective distortion to simulate real camera angles."""
    width, height = img.size
    
    # Define perspective transformation points
    # Slight keystone effect
    distortion = random.uniform(0.02, 0.08)
    
    # Original corners
    original = [
        (0, 0),
        (width, 0),
        (width, height),
        (0, height)
    ]
    
    # Distorted corners
    offset = int(width * distortion)
    distorted = [
        (random.randint(0, offset), random.randint(0, offset)),
        (width - random.randint(0, offset), random.randint(0, offset)),
        (width - random.randint(0, offset), height - random.randint(0, offset)),
        (random.randint(0, offset), height - random.randint(0, offset))
    ]
    
    # Apply perspective transform (simplified)
    try:
        # Use transform with perspective coefficients
        coeffs = []
        for i in range(4):
            coeffs.extend([distorted[i][0], distorted[i][1]])
        
        # Simple approximation of perspective transform
        return img.transform(
            (width, height),
            Image.Transform.QUAD,
            coeffs,
            Image.Resampling.BILINEAR
        )
    except:
        # Fallback: just return original if transform fails
        return img


def create_natural_texture(width: int, height: int) -> Image.Image:
    """Create natural-looking texture with random variations."""
    img = Image.new('RGB', (width, height))
    pixels = img.load()
    
    # Create base color
    base_r = random.randint(80, 180)
    base_g = random.randint(80, 180)
    base_b = random.randint(80, 180)
    
    # Add natural variation
    for y in range(height):
        for x in range(width):
            # Add random variation with different scales
            variation1 = math.sin(x * 0.1) * math.cos(y * 0.1) * 30
            variation2 = random.randint(-40, 40)
            variation3 = math.sin(x * 0.05 + y * 0.03) * 20
            
            total_variation = variation1 + variation2 + variation3
            
            r = max(0, min(255, base_r + int(total_variation)))
            g = max(0, min(255, base_g + int(total_variation * 0.8)))
            b = max(0, min(255, base_b + int(total_variation * 0.6)))
            
            pixels[x, y] = (r, g, b)
    
    return img


def create_natural_scene(width: int, height: int) -> Image.Image:
    """Create a natural scene with varied lighting and shadows."""
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)
    
    # Create sky gradient (natural lighting variation)
    sky_colors = [
        (random.randint(150, 220), random.randint(180, 240), random.randint(200, 255)),
        (random.randint(100, 180), random.randint(140, 200), random.randint(180, 240))
    ]
    
    # Draw gradient sky
    for y in range(height // 2):
        ratio = y / (height // 2)
        r = int(sky_colors[0][0] * (1 - ratio) + sky_colors[1][0] * ratio)
        g = int(sky_colors[0][1] * (1 - ratio) + sky_colors[1][1] * ratio)
        b = int(sky_colors[0][2] * (1 - ratio) + sky_colors[1][2] * ratio)
        
        # Add some natural variation
        r += random.randint(-10, 10)
        g += random.randint(-10, 10)
        b += random.randint(-10, 10)
        
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # Create ground with natural variation
    ground_base = (random.randint(60, 120), random.randint(80, 140), random.randint(40, 100))
    
    for y in range(height // 2, height):
        for x in range(0, width, 5):  # Draw in strips for efficiency
            # Natural ground variation
            variation = random.randint(-30, 30)
            r = max(0, min(255, ground_base[0] + variation))
            g = max(0, min(255, ground_base[1] + variation))
            b = max(0, min(255, ground_base[2] + variation))
            
            draw.line([(x, y), (x + 5, y)], fill=(r, g, b))
    
    # Add some natural objects with shadows
    for _ in range(random.randint(2, 5)):
        # Object position
        obj_x = random.randint(width // 4, 3 * width // 4)
        obj_y = random.randint(height // 2, 3 * height // 4)
        obj_size = random.randint(20, 60)
        
        # Object color (natural, muted)
        obj_color = (
            random.randint(40, 120),
            random.randint(60, 140),
            random.randint(30, 100)
        )
        
        # Draw object (irregular shape)
        points = []
        for i in range(6):
            angle = 2 * math.pi * i / 6
            radius = obj_size + random.randint(-10, 10)
            x = obj_x + radius * math.cos(angle)
            y = obj_y + radius * math.sin(angle)
            points.append((x, y))
        
        draw.polygon(points, fill=obj_color)
        
        # Add shadow (offset and darker)
        shadow_points = [(x + 5, y + 5) for x, y in points]
        shadow_color = tuple(max(0, c - 50) for c in obj_color)
        draw.polygon(shadow_points, fill=shadow_color)
    
    return img


def create_product_like_image(width: int, height: int) -> Image.Image:
    """Create an image that looks like a real product photo."""
    img = Image.new('RGB', (width, height), color=(240, 240, 240))
    draw = ImageDraw.Draw(img)
    
    # Create background with subtle gradient (natural lighting)
    for y in range(height):
        ratio = y / height
        brightness = int(240 - ratio * 40 + random.randint(-10, 10))
        brightness = max(200, min(255, brightness))
        
        for x in range(0, width, 10):
            # Add horizontal variation too
            x_ratio = x / width
            x_brightness = brightness + int((x_ratio - 0.5) * 20)
            x_brightness = max(200, min(255, x_brightness))
            
            color = (x_brightness, x_brightness, x_brightness)
            draw.line([(x, y), (x + 10, y)], fill=color)
    
    # Add main "product" shape with natural imperfections
    center_x, center_y = width // 2, height // 2
    product_size = min(width, height) // 3
    
    # Product base color
    product_colors = [
        (random.randint(100, 200), random.randint(50, 150), random.randint(50, 150)),
        (random.randint(50, 150), random.randint(100, 200), random.randint(50, 150)),
        (random.randint(50, 150), random.randint(50, 150), random.randint(100, 200))
    ]
    product_color = random.choice(product_colors)
    
    # Draw product with slight irregularities
    for angle in range(0, 360, 5):
        radius = product_size + random.randint(-5, 5)
        x = center_x + radius * math.cos(math.radians(angle))
        y = center_y + radius * math.sin(math.radians(angle))
        
        # Vary color slightly for natural look
        varied_color = tuple(
            max(0, min(255, c + random.randint(-20, 20))) 
            for c in product_color
        )
        
        draw.ellipse([x-2, y-2, x+2, y+2], fill=varied_color)
    
    # Add highlight (natural reflection)
    highlight_x = center_x - product_size // 3
    highlight_y = center_y - product_size // 3
    highlight_size = product_size // 4
    
    for i in range(highlight_size):
        alpha = 1 - (i / highlight_size)
        brightness = int(255 * alpha)
        highlight_color = (brightness, brightness, brightness)
        
        draw.ellipse([
            highlight_x - i, highlight_y - i,
            highlight_x + i, highlight_y + i
        ], outline=highlight_color)
    
    return img


def apply_realistic_processing(img: Image.Image) -> Image.Image:
    """Apply realistic camera processing effects."""
    # Add slight blur (camera focus imperfection)
    if random.random() < 0.3:
        img = img.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.5, 1.5)))
    
    # Adjust contrast naturally
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(random.uniform(0.9, 1.2))
    
    # Adjust brightness naturally
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(random.uniform(0.9, 1.1))
    
    # Adjust saturation naturally
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(random.uniform(0.8, 1.2))
    
    return img


def generate_realistic_images(count: int) -> List[np.ndarray]:
    """
    Generate realistic-looking images for training.
    
    Args:
        count: Number of images to generate
        
    Returns:
        List of image arrays
    """
    images = []
    
    generators = [
        create_natural_texture,
        create_natural_scene,
        create_product_like_image
    ]
    
    for i in range(count):
        # Random image size
        width = random.randint(200, 400)
        height = random.randint(200, 400)
        
        # Choose generator
        if i < len(generators):
            generator = generators[i % len(generators)]
        else:
            generator = random.choice(generators)
        
        try:
            # Generate base image
            img = generator(width, height)
            
            # Apply realistic effects
            img = apply_realistic_processing(img)
            
            # Add camera noise
            img = add_camera_noise(img, intensity=random.uniform(0.05, 0.15))
            
            # Add perspective distortion occasionally
            if random.random() < 0.4:
                img = add_perspective_distortion(img)
            
            # Convert to numpy array
            img_array = np.array(img)
            images.append(img_array)
            
        except Exception as e:
            print(f"Error generating realistic image {i}: {e}")
            # Create fallback natural image
            fallback = Image.new('RGB', (width, height))
            draw = ImageDraw.Draw(fallback)
            
            # Simple natural gradient
            for y in range(height):
                brightness = int(200 + (y / height) * 55 + random.randint(-20, 20))
                brightness = max(0, min(255, brightness))
                draw.line([(0, y), (width, y)], fill=(brightness, brightness, brightness))
            
            # Add noise
            fallback = add_camera_noise(fallback, 0.1)
            images.append(np.array(fallback))
    
    print(f"Generated {len(images)} realistic images")
    return images


if __name__ == "__main__":
    # Test generation
    test_images = generate_realistic_images(5)
    print(f"Test generated {len(test_images)} images")
    for i, img in enumerate(test_images):
        print(f"Image {i}: shape {img.shape}, dtype {img.dtype}")