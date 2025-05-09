import numpy as np
import cv2

class DistanceCalculator:
    def __init__(self):
        """Initialize the distance calculator."""
        self.camera_matrix = None
        self.dist_coeffs = None
        self.reference_distance = None
        self.reference_pixels = None
        
    def calibrate_camera(self, calibration_images):
        """Calibrate the camera using a set of calibration images."""
        # Prepare object points (0,0,0), (1,0,0), (1,1,0), (0,1,0)
        objp = np.zeros((6*7,3), np.float32)
        objp[:,:2] = np.mgrid[0:7,0:6].T.reshape(-1,2)
        
        # Arrays to store object points and image points
        objpoints = []  # 3D points in real world space
        imgpoints = []  # 2D points in image plane
        
        for img in calibration_images:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            ret, corners = cv2.findChessboardCorners(gray, (7,6), None)
            
            if ret:
                objpoints.append(objp)
                imgpoints.append(corners)
                
        if objpoints and imgpoints:
            ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
                objpoints, imgpoints, gray.shape[::-1], None, None
            )
            self.camera_matrix = mtx
            self.dist_coeffs = dist
            return True
        return False
    
    def set_reference(self, reference_distance, reference_pixels):
        """Set reference measurements for distance calculation."""
        self.reference_distance = reference_distance
        self.reference_pixels = reference_pixels
        
    def calculate_distance(self, pixel_distance):
        """Calculate real-world distance based on pixel measurements."""
        if not self.reference_distance or not self.reference_pixels:
            return None
            
        # Simple proportional calculation
        return (pixel_distance * self.reference_distance) / self.reference_pixels
    
    def estimate_shot_distance(self, start_point, end_point):
        """Estimate the distance of a shot based on start and end points."""
        if not self.reference_distance or not self.reference_pixels:
            return None
            
        # Calculate pixel distance
        pixel_distance = np.sqrt(
            (end_point[0] - start_point[0])**2 +
            (end_point[1] - start_point[1])**2
        )
        
        return self.calculate_distance(pixel_distance) 