# app/main.py
import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import Response

app = FastAPI(title="CamScanner Clone API", version="0.2.0")

def detect_edges(image_bytes:bytes) -> bytes:
    """
    Takes raw image bytes, detects edges, and returns the processed image bytes.
    """
    # 1. Convert bytes to a numpy array
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image file")

    # 2. Preprocessing: Grayscale and Blur
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5,5),0)

    # 3. Edge Detection using Canny
    # Thresholds: 50 (min) and 150 (max) determine sensitivity
    edged = cv2.Canny(blurred, 50, 150)

    # 4. Encode the result back to JPEG bytes to send over the API
    _, encoded_img = cv2.imencode('.jpg',edged)
    return encoded_img.tobytes()


@app.post("/detect-edges")
async def detect_edges_endpoint(file: UploadFile = File(...)):
    """
    Upload an image to get its edge-detected version.
    """
    try:
        # Read the file content
        contents = await file.read()

        # Process the image
        processed_bytes = detect_edges(contents)
        return Response(content=processed_bytes, media_type="image/jpeg")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

