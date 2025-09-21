"""Explanation engine for authenticity detection results."""

import numpy as np
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

# Feature indices for interpretation
FEATURE_NAMES = [
    # Edge features (0-3)
    'edge_density', 'laplacian_var', 'grad_mean', 'grad_std',
    # Color features (4-16)
    'r_mean', 'r_std', 'r_skew',
    'g_mean', 'g_std', 'g_skew', 
    'b_mean', 'b_std', 'b_skew',
    'sat_mean', 'sat_std', 'val_mean', 'val_std', 'color_entropy',
    # Compression features (17-22)
    'dct_mean', 'dct_std', 'dct_max', 'var_mean', 'var_std', 'var_ratio',
    # Noise/texture features (23-30)
    'noise_energy', 'noise_mean', 'texture_mean', 'texture_std',
    'freq_ring1', 'freq_ring2', 'freq_ring3', 'periodicity'
]

# Thresholds for feature anomaly detection (approximate values)
FEATURE_THRESHOLDS = {
    'edge_density': {'low': 0.02, 'high': 0.15},
    'laplacian_var': {'low': 50, 'high': 500},
    'color_entropy': {'low': 6.0, 'high': 8.0},
    'noise_energy': {'low': 10, 'high': 100},
    'texture_mean': {'low': 20, 'high': 200},
    'periodicity': {'low': 0.8, 'high': 1.5},
    'dct_mean': {'low': 100, 'high': 1000},
    'var_ratio': {'low': 0.3, 'high': 2.0}
}


def analyze_feature_anomalies(features: np.ndarray) -> Dict[str, str]:
    """
    Analyze feature vector for anomalies that indicate synthetic content.
    
    Args:
        features: Feature vector
        
    Returns:
        Dictionary mapping feature names to anomaly descriptions
    """
    anomalies = {}
    
    try:
        if len(features) != len(FEATURE_NAMES):
            logger.warning(f"Feature vector length mismatch: {len(features)} vs {len(FEATURE_NAMES)}")
            return anomalies
        
        # Check edge features
        edge_density = features[0]
        if edge_density < FEATURE_THRESHOLDS['edge_density']['low']:
            anomalies['edges'] = "unusually smooth edges"
        elif edge_density > FEATURE_THRESHOLDS['edge_density']['high']:
            anomalies['edges'] = "overly sharp artificial edges"
        
        # Check sharpness
        laplacian_var = features[1]
        if laplacian_var < FEATURE_THRESHOLDS['laplacian_var']['low']:
            anomalies['sharpness'] = "unnaturally uniform sharpness"
        elif laplacian_var > FEATURE_THRESHOLDS['laplacian_var']['high']:
            anomalies['sharpness'] = "excessive artificial sharpening"
        
        # Check color entropy
        color_entropy = features[16]
        if color_entropy < FEATURE_THRESHOLDS['color_entropy']['low']:
            anomalies['colors'] = "limited color palette typical of generated images"
        
        # Check noise characteristics
        noise_energy = features[23]
        if noise_energy < FEATURE_THRESHOLDS['noise_energy']['low']:
            anomalies['noise'] = "suspiciously low noise levels"
        
        # Check texture patterns
        texture_mean = features[25]
        periodicity = features[30]
        if texture_mean < FEATURE_THRESHOLDS['texture_mean']['low']:
            anomalies['texture'] = "overly smooth textures"
        if periodicity > FEATURE_THRESHOLDS['periodicity']['high']:
            anomalies['patterns'] = "repetitive artificial patterns detected"
        
        # Check compression artifacts
        dct_mean = features[17]
        var_ratio = features[22]
        if dct_mean < FEATURE_THRESHOLDS['dct_mean']['low']:
            anomalies['compression'] = "unusual compression characteristics"
        if var_ratio < FEATURE_THRESHOLDS['var_ratio']['low']:
            anomalies['blocks'] = "uniform block patterns suggest artificial generation"
        
        # Check color distribution
        r_std, g_std, b_std = features[5], features[8], features[11]
        color_uniformity = np.std([r_std, g_std, b_std])
        if color_uniformity < 5.0:
            anomalies['color_dist'] = "unnaturally uniform color distribution"
        
        # Check saturation patterns
        sat_mean, sat_std = features[13], features[14]
        if sat_mean > 200 and sat_std < 20:
            anomalies['saturation'] = "artificially high and uniform saturation"
        
    except Exception as e:
        logger.error(f"Error analyzing feature anomalies: {e}")
    
    return anomalies


def generate_guidance_messages(label: str, synthetic_prob: float) -> List[str]:
    """
    Generate actionable guidance based on classification result.
    
    Args:
        label: Classification label
        synthetic_prob: Synthetic probability score
        
    Returns:
        List of guidance messages
    """
    guidance = []
    
    if label == "synthetic":
        guidance.extend([
            "Needs Real Proof — Consider uploading real-world photos (multiple angles, material close-ups, scale references).",
            "Avoid oversmoothing and uniform lighting.",
            "Include natural imperfections and realistic shadows."
        ])
        
        if synthetic_prob > 0.9:
            guidance.append("Very high confidence this is AI-generated content.")
        
    elif label == "suspicious":
        guidance.extend([
            "Looks Suspicious — Lighting/texture patterns are atypical.",
            "Add more real photos to increase confidence.",
            "Consider including photos with natural backgrounds and varied lighting."
        ])
        
        if synthetic_prob > 0.6:
            guidance.append("Several indicators suggest possible AI generation.")
        else:
            guidance.append("Some unusual patterns detected, but may be due to heavy processing.")
            
    else:  # authentic
        guidance.extend([
            "Verified — Signals look consistent with real photography.",
            "Good natural variation in lighting and texture detected."
        ])
        
        if synthetic_prob < 0.05:
            guidance.append("Strong indicators of authentic photography.")
    
    return guidance


def reasons_from_features(features: np.ndarray, extras: Optional[Dict] = None) -> List[str]:
    """
    Generate human-readable reasons for classification decision.
    
    Args:
        features: Feature vector
        extras: Additional context (synthetic_prob, label, metadata)
        
    Returns:
        List of reason strings
    """
    reasons = []
    
    try:
        # Get basic context
        if extras:
            label = extras.get('label', 'unknown')
            synthetic_prob = extras.get('synthetic_prob', 0.5)
            metadata = extras.get('metadata', {})
        else:
            label = 'unknown'
            synthetic_prob = 0.5
            metadata = {}
        
        # Analyze feature anomalies
        anomalies = analyze_feature_anomalies(features)
        
        # Convert anomalies to reasons
        for feature_type, description in anomalies.items():
            reasons.append(f"Detected {description}")
        
        # Add guidance messages
        guidance = generate_guidance_messages(label, synthetic_prob)
        reasons.extend(guidance)
        
        # Add technical details if available
        if metadata.get('resized'):
            reasons.append("Image was resized for analysis")
        
        # Add confidence-based reasoning
        if synthetic_prob > 0.8:
            reasons.append("Multiple strong indicators of artificial generation")
        elif synthetic_prob > 0.6:
            reasons.append("Several suspicious patterns detected")
        elif synthetic_prob > 0.4:
            reasons.append("Mixed signals - some artificial characteristics present")
        elif synthetic_prob > 0.2:
            reasons.append("Mostly natural characteristics with minor anomalies")
        else:
            reasons.append("Strong natural photography indicators")
        
        # Ensure we have at least some basic reasoning
        if not reasons:
            if label == "synthetic":
                reasons.append("Pattern analysis suggests artificial generation")
            elif label == "suspicious":
                reasons.append("Some unusual characteristics detected")
            else:
                reasons.append("Analysis indicates natural photography")
        
        # Add disclaimer
        reasons.append("This tool suggests, doesn't punish. Human review recommended.")
        
    except Exception as e:
        logger.error(f"Error generating reasons: {e}")
        reasons = [
            f"Analysis completed with classification: {label}",
            "This tool suggests, doesn't punish. Human review recommended."
        ]
    
    return reasons[:8]  # Limit to 8 reasons for UI clarity