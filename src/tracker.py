# File: src/tracker.py
import numpy as np
from collections import deque
from deep_sort_realtime.deepsort_tracker import DeepSort
from detectors import Det

class Tracker:
    """
    Uses DeepSort to track ball and hoop across frames.
    Maintains trajectory for the ball ID.
    """
    def __init__(self):
        # Initialize DeepSort with default weights
        self.deepsort = DeepSort(max_age=30)
        self.trajectory = {}  # id -> deque of (x, y)
        self.max_len = 64      # max length of trajectory

    def update(self, detections: List[Det]) -> List[Det]:
        # Convert Det to DeepSort format: [x1,y1,x2,y2,confidence,class]
        raw = []
        for det in detections:
            x1, y1, x2, y2 = det.bbox
            raw.append((det.bbox, det.confidence, det.cls))

        tracks = self.deepsort.update_tracks(raw, embed_results=False)
        out: List[Det] = []
        for track in tracks:
            if not track.is_confirmed():
                continue
            bbox = track.to_ltrb()  # left, top, right, bottom
            tid = track.track_id
            cls = track.get_det_class()
            center = ((bbox[0] + bbox[2]) // 2, (bbox[1] + bbox[3]) // 2)

            # maintain trajectory
            if cls == 'ball':
                self.trajectory.setdefault(tid, deque(maxlen=self.max_len)).append(center)

            out.append(Det(cls, (int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])), track.det_confidence))
        return out

    def clear_trajectory(self, track_id: int):
        self.trajectory.pop(track_id, None)