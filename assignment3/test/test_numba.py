import numpy.testing as nt
from in3110_instapy.numba_filters import numba_color2gray, numba_color2sepia
import numpy as np

def test_color2gray(image, reference_gray):
    # Run function
    gray_image = numba_color2gray(image)
    
    # Verify grayscale image properties
    assert len(gray_image.shape) == 2, "Grayscale image should have 2 dimensions"
    assert gray_image.dtype == np.uint8, "Grayscale image should have dtype uint8"
    
    # Validate grayscale values for randomly selected pixels
    np.random.seed(1)
    H, W = gray_image.shape
    for _ in range(5):
        i, j = np.random.randint(H), np.random.randint(W)
        r, g, b = image[i, j]
        expected_gray_value = int(r * 0.21 + g * 0.72 + b * 0.07)
        assert gray_image[i, j] == expected_gray_value, f"Grayscale value at pixel ({i}, {j}) is incorrect"
    nt.assert_allclose(gray_image, reference_gray)

def test_color2sepia(image, reference_sepia):
    # Run function
    sepia_image = numba_color2sepia(image)
    
    # Verify sepia image properties
    assert len(sepia_image.shape) == 3, "Sepia image should have 3 dimensions"
    assert sepia_image.dtype == np.uint8, "Sepia image should have dtype uint8"
    
    # Validate pixel values using sepia matrix transformation for randomly selected pixels
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
        nt.assert_allclose(sepia_image[i, j, :], expected_value, atol=1)  # Set a tolerance for numerical comparisons
    nt.assert_allclose(sepia_image, reference_sepia)