"""numpy implementation of image filters"""
from __future__ import annotations

import numpy as np


def numpy_color2gray(image: np.array) -> np.array:
    """Convert rgb pixel array to grayscale

    Args:
        image (np.array)
    Returns:
        np.array: gray_image
    """
    # Grayscale coefficients
    red_coefficient = 0.21
    green_coefficient = 0.72
    blue_coefficient = 0.07

    gray_image = np.empty_like(image)

    # Use numpy slicing and vectorized operations for efficient grayscale conversion
    gray_image = np.dot(image[..., :3], [red_coefficient, green_coefficient, blue_coefficient])
    
    # Ensure the values are within the valid range [0, 255] and convert to uint8
    gray_image = np.clip(gray_image, 0, 255).astype(np.uint8)

    return gray_image


def numpy_color2sepia(image: np.array, k: float = 1) -> np.array:
    """Convert rgb pixel array to sepia

    Args:
        image (np.array)
        k (float): amount of sepia (optional)

    The amount of sepia is given as a fraction, k=0 yields no sepia while
    k=1 yields full sepia.

    (note: implementing 'k' is a bonus task,
        you may ignore it)

    Returns:
        np.array: sepia_image
    """

    if not 0 <= k <= 1:
        # validate k (optional)
        raise ValueError(f"k must be between [0-1], got {k=}")

    # define sepia matrix (optional: with stepless sepia changes)
    sepia_matrix = np.array([
        [0.393, 0.769, 0.189],
        [0.349, 0.686, 0.168],
        [0.272, 0.534, 0.131]
    ])

    sepia_image = np.dot(image, sepia_matrix.T) * k

    # HINT: For version without adaptive sepia filter, use the same matrix as in the pure python implementation
    # any way works, but you could use an Einstein sum to apply pixel transform matrix
    # or a tensor dot product, for example
    sepia_image = np.clip(sepia_image, 0, 255).astype(np.uint8)

    # Check which entries have a value greater than 255 and set it to 255 since we can not display values bigger than 255
    sepia_image[np.where(sepia_image > 255)] = 255

    # Return image (make sure it's the right type!)
    return sepia_image
