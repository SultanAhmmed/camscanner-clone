import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def sample_image_bytes():
    img = np.ones((500, 500, 3), dtype=np.uint8) * 255
    cv2.rectangle(img, (50, 50), (450, 450), (0, 0, 0), 2)
    _, encoded = cv2.imencode('.jpg', img)
    return encoded.tobytes()

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_scan_document_single_file(client, sample_image_bytes):
    response = client.post(
        "/scan-document?mode=scan",
        files={"file": ("test.jpg", sample_image_bytes, "image/jpeg")}
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpeg"

def test_scan_to_pdf_multiple_files(client, sample_image_bytes):
    response = client.post(
        "/scan-to-pdf?mode=scan",
        files=[
            ("files", ("page1.jpg", sample_image_bytes, "image/jpeg")),
            ("files", ("page2.jpg", sample_image_bytes, "image/jpeg")),
        ]
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")

def test_invalid_mode(client, sample_image_bytes):
    response = client.post(
        "/scan-document?mode=invalid_mode",
        files={"file": ("test.jpg", sample_image_bytes, "image/jpeg")}
    )
    assert response.status_code == 400
