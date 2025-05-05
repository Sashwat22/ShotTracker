# File: src/detectors.py
import cv2
from ultralytics import YOLO
import numpy as np
from typing import List, Tuple

# A detection result: bounding box and class
class Det:
    def __init__(self, cls: str, bbox: Tuple[int, int, int, int], confidence: float):
        self.cls = cls  # 'ball' or 'hoop'
        self.bbox = bbox  # (x1, y1, x2, y2)
        self.confidence = confidence

class Detector:
    """
    Wraps YOLOv8 model inference for ball and hoop detection.
    """
    def __init__(self, model_path: str = 'models/basketball.pt'):
        # Load a fine-tuned YOLOv8-n model
        self.model = YOLO(model_path)

    def detect(self, frame: np.ndarray) -> List[Det]:
        results = self.model(frame)[0]
        detections: List[Det] = []
        for *box, conf, cls in results.boxes.data.tolist():
            x1, y1, x2, y2 = map(int, box)
            cls_name = 'ball' if int(cls) == 0 else 'hoop'
            detections.append(Det(cls_name, (x1, y1, x2, y2), float(conf)))
        return detections