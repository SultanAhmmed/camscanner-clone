# app/main.py
import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import Response

app = FastAPI(title="CamScanner Clone API", version="0.2.0")


def order_points(pts):
    """
    Orders 4 points in the order: Top-Left, Top-Right, Bottom-Right, Bottom-Left
    """
    rect = np.zeros((4, 2), dtype="float32")
    print(rect)

    # Top-left has the smallest sum of (x + y)
    # Bottom-right has the largest sum of (x + y)
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    # Top-right has the smallest difference of (x - y)
    # Bottom-left has the largest difference of (x - y)
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    return rect

def four_point_transform(image, pts):
    """
    Applies a perspective transform to get a top-down view of the document.
    """
    # 1. Got the ordered points
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    # 2. Compute the width of the new image
    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    maxWidth = max(int(widthA), int(widthB))

    # 3. Compute the height of the new image
    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
    maxHeight = max(int(heightA),int(heightB))

    # 4. Define the destination points for the "flattened" image
    dst  = np.array([
        [0, 0],
        [maxWidth-1, 0],
        [maxWidth-1, maxHeight-1],
        [0, maxHeight-1]
    ],dtype="float32")

    # 5. Compute the perspective transform matrix and apply it
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

    return warped

def process_document(image_bytes: bytes) -> bytes:
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
    img_resized = cv2.resize(img , (int(img.shape[1]/ratio),500))

    # 2. Preprocessing: Grayscale and Blur
    gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 75, 200)

    # 3. Find contours in the edge map
    # RETR_LIST gets all contours, CHAIN_APPROX_SIMPLE compresses them
    contours, _ = cv2.findContours(edged.copy(),cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    # Sort contours by area, largest first
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

    screen_cnt = None

    # 4. Loop over the largest contours to find one with 4 corners
    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02*peri, True)

        # If our approximated contour has four points, we found our screen
        if len(approx) == 4:
            screen_cnt = approx
            break

    # 5. Apply the perspective transform
    if screen_cnt is not None:
        # Multiply the corner points by the ratio to map them back to the original image size
        warped = four_point_transform(orig, screen_cnt.reshape(4,2) * ratio)
    else:
        # If no document is found, just return the original image
        warped = orig

    # 6. Encode the result back to JPEG bytes
    _, encoded_img = cv2.imencode(".jpg", warped)
    return encoded_img.tobytes()


@app.post("/scan-document")
async def scan_document_endpoint(file: UploadFile = File(...)):
    """
    Upload an image of a document to get a flattened, top-down scanned version.
    """
    try:
        # Read the file content
        contents = await file.read()

        # Process the image
        processed_bytes = process_document(contents)
        return Response(content=processed_bytes, media_type="image/jpeg")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
