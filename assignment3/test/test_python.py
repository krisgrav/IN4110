from in3110_instapy.python_filters import python_color2gray, python_color2sepia
import numpy as np


def test_color2gray(image):
    # Run function
    gray_image = python_color2gray(image)
    
    # Verify grayscale image properties
    assert len(gray_image.shape) == 2, "Grayscale image should have 2 dimensions"
    assert gray_image.dtype == np.uint8, "Grayscale image should have dtype uint8"
    
    # Validate grayscale values for 5 randomly selected pixels
    np.random.seed(1)
    H, W, _ = image.shape
    for _ in range(5):
        i, j = np.random.randint(H), np.random.randint(W)
        r, g, b = image[i, j]
        expected_gray_value = int(r * 0.21 + g * 0.72 + b * 0.07)
        assert gray_image[i, j] == expected_gray_value, f"Grayscale value at pixel ({i}, {j}) is incorrect"


def test_color2sepia(image):
    # Run function
    sepia_image = python_color2sepia(image)
    
    # Verify sepia image properties
    assert len(sepia_image.shape) == 3, "Sepia image should have 3 dimensions"
    assert sepia_image.dtype == np.uint8, "Sepia image should have dtype uint8"
    
    # Verify pixel values using sepia matrix transformation for 5 randomly selected pixels
    sepia_matrix = np.array([
        [0.393, 0.769, 0.189],
        [0.349, 0.686, 0.168],
        [0.272, 0.534, 0.131]
    ])
    
    np.random.seed(1)
    H, W, _ = image.shape
    for _ in range(5):
        i, j = np.random.randint(H), np.random.randint(W)
        expected_value = np.dot(image[i, j, :], sepia_matrix.T)
        expected_value = np.clip(expected_value, 0, 255).astype(np.uint8)
        assert np.array_equal(sepia_image[i, j, :], expected_value), f"Sepia value at pixel ({i}, {j}) is incorrect"
