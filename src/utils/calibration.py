# File: src/utils/calibration.py
import cv2
import numpy as np

class Calibration:
    """
    Computes homography from pixel to real-world court coordinates.
    """
    def __init__(self):
        self.H = None

    def compute_homography(self, src_points: np.ndarray, dst_points: np.ndarray):
        # src_points: 4x2 pixel coords, dst_points: 4x2 real-world coords (meters)
        self.H, _ = cv2.findHomography(src_points, dst_points, method=cv2.RANSAC)

    def pixels_to_meters(self, pt: Tuple[int, int]) -> Tuple[float, float]:
        if self.H is None:
            raise ValueError("Homography not computed")
        px = np.array([pt[0], pt[1], 1.0])
        wx = self.H.dot(px)
        wx /= wx[2]
        return float(wx[0]), float(wx[1])