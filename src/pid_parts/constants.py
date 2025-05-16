"""
Configuration constants used throughout the PID parts package.

This module defines central configuration values that control the behavior
of image processing, tiling, and PDF conversion. These values can be adjusted
to optimize performance and accuracy for different types of PID drawings.
"""

# Size of each square tile in pixels
# Larger values process more content at once but may exceed model context limits
TILE_PX: int = 1200

# Fraction of overlap between adjacent tiles (0.0-1.0)
# Higher values help detect elements that might be split across tile boundaries
# 0.15 (15%) follows SAHI (Slicing Aided Hyper Inference) guidelines
OVERLAP: float = 0.15

# Resolution for PDF to image conversion in dots per inch
# Higher values produce larger, more detailed images but require more memory
DPI: int = 300
