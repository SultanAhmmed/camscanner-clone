import cv2
import numpy as np
import pytest
from src import process_document
from src import four_point_transform, order_points

def test_order_points():
    """Test that points are ordered: TL, TR, BR, BL"""
    # Create 4 random points
    pts = np.array([
        [100, 100],  # should be TL (smallest x+y)
        [200, 100],  # should be TR (smallest x-y)
        [200, 200],  # should be BR (largest x+y)
        [100, 200],  # should be BL (largest x-y)
    ], dtype="float32")

    ordered = order_points.order_points(pts)

    # Verify the order
    assert np.array_equal(ordered[0], [100, 100])  # TL
    assert np.array_equal(ordered[1], [200, 100])  # TR
    assert np.array_equal(ordered[2], [200, 200])  # BR
    assert np.array_equal(ordered[3], [100, 200])  # BL

def test_process_document_with_valid_image():
    """Test that process_document returns bytes for a valid image"""
    # Create a simple test image (white with a black rectangle)
    img = np.ones((500, 500, 3), dtype=np.uint8) * 255
    cv2.rectangle(img, (50, 50), (450, 450), (0, 0, 0), 2)

    # Encode to JPEG bytes
    _, encoded = cv2.imencode('.jpg', img)
    image_bytes = encoded.tobytes()

    # Test all modes
    for mode in ["color", "gray", "scan", "enhanced"]:
        result = process_document.process_document(image_bytes, mode)
        assert isinstance(result, bytes)
        assert len(result) > 0

def test_process_document_invalid_image():
    """Test that invalid image bytes raise an error"""
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc_info:
        process_document.process_document(b"not an image", "scan")
    assert exc_info.value.status_code == 400
