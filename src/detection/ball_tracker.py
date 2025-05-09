import cv2
import numpy as np
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort

class BallTracker:
    def __init__(self, model_path=None):
        """Initialize the ball tracker with YOLO and DeepSORT."""
        self.model = YOLO('yolov8n.pt') if model_path is None else YOLO(model_path)
        self.tracker = DeepSort(max_age=30)
        self.trajectory = []
        
    def detect_ball(self, frame):
        """Detect basketball in the frame using YOLO."""
        results = self.model(frame, classes=[32])  # 32 is the COCO class ID for sports ball
        return results[0].boxes.data.cpu().numpy()
    
    def track_ball(self, frame):
        """Track the ball using DeepSORT and update trajectory."""
        detections = self.detect_ball(frame)
        tracks = self.tracker.update_tracks(detections, frame=frame)
        
        for track in tracks:
            if track.is_confirmed():
                x1, y1, x2, y2 = track.to_tlbr()
                center = ((x1 + x2) / 2, (y1 + y2) / 2)
                self.trajectory.append(center)
                
        return tracks
    
    def get_trajectory(self):
        """Return the current ball trajectory."""
        return self.trajectory
    
    def reset_trajectory(self):
        """Reset the trajectory tracking."""
        self.trajectory = [] 