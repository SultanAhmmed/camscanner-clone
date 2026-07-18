import numpy as np
import cv2
from fastapi import HTTPException
from src.four_point_transform import four_point_transform

def process_document(image_bytes: bytes, mode: str) -> bytes:
    """
    Takes raw image bytes, finds the document, flattens it, and returns it.
    """
    # 1. Convert bytes to a numpy array
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image file")

    # Keep a copy of the original dimensions for resizing later if needed
    ratio = img.shape[0] / 500.0
    orig = img.copy()

    # Resize for faster processing
    img_resized = cv2.resize(img, (int(img.shape[1] / ratio), 500))

    # 2. Preprocessing: Grayscale and Blur
    gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 75, 200)

    # 3. Find contours in the edge map
    # RETR_LIST gets all contours, CHAIN_APPROX_SIMPLE compresses them
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    # Sort contours by area, largest first
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

    screen_cnt = None

    # 4. Loop over the largest contours to find one with 4 corners
    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)

        # If our approximated contour has four points, we found our screen
        if len(approx) == 4:
            screen_cnt = approx
            break

    # 5. Apply the perspective transform
    if screen_cnt is not None:
        # Multiply the corner points by the ratio to map them back to the original image size
        warped = four_point_transform(orig, screen_cnt.reshape(4, 2) * ratio)
    else:
        # If no document is found, just return the original image
        warped = orig

    if mode == "original":
        result = orig

    elif mode == "color":
        result = warped

    elif mode == "gray":
        result = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)

    elif mode == "scan":
        gray_warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)

        # 6. Apply Adaptive Thresholding to make text crisp
        result = cv2.adaptiveThreshold(
            gray_warped, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 35, 15
        )
    elif mode == "enhanced":
        gray_warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
        # CLAHE improves contrast locally without amplifying noise
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        result = clahe.apply(gray_warped)
    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid mode. Choose from: color, gray, scan, enhanced",
        )

    # 7. Encode the result back to JPEG bytes
    _, encoded_img = cv2.imencode(".jpg", result)
    return encoded_img.tobytes()
