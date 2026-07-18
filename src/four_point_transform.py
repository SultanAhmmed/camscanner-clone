import numpy as np
import cv2
from src.order_points import order_points

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
    maxHeight = max(int(heightA), int(heightB))

    # 4. Define the destination points for the "flattened" image
    dst = np.array(
        [[0, 0], [maxWidth - 1, 0], [maxWidth - 1, maxHeight - 1], [0, maxHeight - 1]],
        dtype="float32",
    )

    # 5. Compute the perspective transform matrix and apply it
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

    return warped
