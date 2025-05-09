import cv2
from ultralytics import YOLO

class YOLODetector:
    def __init__(self, model_path="best.pt"):
        self.model_path = model_path
        self.model = YOLO(self.model_path)
        self.ball_conf_thresh = 0.5
        self.hoop_conf_thresh = 0.3
    
    def load_model(self, model_path):
        """Load a new YOLO model"""
        try:
            self.model_path = model_path
            self.model = YOLO(self.model_path)
            return True, "Model loaded successfully"
        except Exception as e:
            return False, f"Error loading model: {str(e)}"
    
    def detect(self, frame):
        """Run detection on a frame and return ball and hoop bounding boxes"""
        if frame is None:
            return None, None
            
        results = self.model(frame, verbose=False)
        
        ball_bbox = None
        hoop_bbox = None
        
        for r in results:
            boxes = r.boxes
            for box in boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                
                # Assuming class 0 is ball and class 1 is hoop
                if cls == 0 and conf > self.ball_conf_thresh:
                    if ball_bbox is None or conf > ball_bbox[4]:
                        ball_bbox = (x1, y1, x2, y2, conf)
                elif cls == 1 and conf > self.hoop_conf_thresh:
                     if hoop_bbox is None or conf > hoop_bbox[4]:
                        hoop_bbox = (x1, y1, x2, y2, conf)
                        
        return ball_bbox, hoop_bbox
        
    def draw_detections(self, frame, ball_bbox, hoop_bbox):
        """Draw bounding boxes on the frame"""
        annotated_frame = frame.copy()
        
        # Draw the ball with a clean white circle
        if ball_bbox:
            ball_x1, ball_y1, ball_x2, ball_y2, ball_conf = ball_bbox
            ball_center_x = (ball_x1 + ball_x2) // 2
            ball_center_y = (ball_y1 + ball_y2) // 2
            ball_center = (ball_center_x, ball_center_y)
            
            # Draw the current ball with a clean white circle
            cv2.circle(annotated_frame, ball_center, 10, (255, 255, 255), 2)
            
            # Add confidence with clean styling
            conf_text = f"{ball_conf:.2f}"
            cv2.putText(annotated_frame, 
                       conf_text, 
                       (ball_x1, ball_y1 - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 
                       0.5, 
                       (255, 255, 255), 
                       1)
        
        # Draw the hoop with a simple, clean rectangle
        if hoop_bbox:
            hoop_x1, hoop_y1, hoop_x2, hoop_y2, hoop_conf = hoop_bbox
            
            # Draw hoop bounding box - white for clean look
            cv2.rectangle(annotated_frame, (hoop_x1, hoop_y1), (hoop_x2, hoop_y2), (255, 255, 255), 2)
            
            # Add rim visualization
            rim_y = hoop_y1 + int((hoop_y2 - hoop_y1) * 0.5)
            rim_left = hoop_x1 + int((hoop_x2 - hoop_x1) * 0.2)
            rim_right = hoop_x2 - int((hoop_x2 - hoop_x1) * 0.2)
            cv2.line(annotated_frame, (rim_left, rim_y), (rim_right, rim_y), (200, 200, 200), 2)
            
        return annotated_frame 