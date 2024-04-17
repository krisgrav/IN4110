"""pure Python implementation of image filters"""
from __future__ import annotations

import numpy as np


def python_color2gray(image: np.array) -> np.array:
    """Convert rgb pixel array to grayscale

    Args:
        image (np.array)
    Returns:
        np.array: gray_image
    """
    red_coefficient = 0.21
    green_coefficient = 0.72
    blue_coefficient = 0.07
    
    # Get the shape of the input image
    height, width, _ = image.shape
    
    # Create an empty array for the grayscale image
    gray_image = np.empty((height, width), dtype=np.uint8)
    
    # Iterate through the pixels and apply the grayscale transform
    for i in range(height):
        for j in range(width):
            # Get RGB values of the current pixel
            red = image[i, j, 0]
            green = image[i, j, 1]
            blue = image[i, j, 2]
            
            # Calculate grayscale intensity using custom coefficients
            gray_intensity = int(red * red_coefficient + green * green_coefficient + blue * blue_coefficient)
            
            # Set grayscale intensity for the current pixel
            gray_image[i, j] = gray_intensity
    return gray_image


def python_color2sepia(image: np.array) -> np.array:
    """Convert rgb pixel array to sepia

    Args:
        image (np.array)
    Returns:
        np.array: sepia_image
    """
    # Sepia matrix
    sepia_matrix = np.array([
        [0.393, 0.769, 0.189],
        [0.349, 0.686, 0.168],
        [0.272, 0.534, 0.131]
    ])


    height, width, _ = image.shape
    
    sepia_image = np.empty_like(image, dtype=np.uint8)
    
    # Iterate through the pixels and apply sepia transformation
    for i in range(height):
        for j in range(width):
            red, green, blue = image[i, j]
            
            # Calculate sepia values using the matrix
            sepia_red = int(min(255, (red * sepia_matrix[0, 0] + green * sepia_matrix[0, 1] + blue * sepia_matrix[0, 2])))
            sepia_green = int(min(255, (red * sepia_matrix[1, 0] + green * sepia_matrix[1, 1] + blue * sepia_matrix[1, 2])))
            sepia_blue = int(min(255, (red * sepia_matrix[2, 0] + green * sepia_matrix[2, 1] + blue * sepia_matrix[2, 2])))
            
            # Set sepia values for the current pixel
            sepia_image[i, j] = [sepia_red, sepia_green, sepia_blue]
    return sepia_image
