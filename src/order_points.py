import numpy as np

def order_points(pts):
    """
    Orders 4 points in the order: Top-Left, Top-Right, Bottom-Right, Bottom-Left
    """
    rect = np.zeros((4, 2), dtype="float32")

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
