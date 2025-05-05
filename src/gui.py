# File: src/gui.py
import cv2
from detectors import Detector
from tracker import Tracker
from stats import ShotStats
from utils.calibration import Calibration

class GUI:
    def __init__(self, source=0):
        self.detector = Detector()
        self.tracker = Tracker()
        self.stats = ShotStats()
        self.calib = Calibration()
        self.cap = cv2.VideoCapture(source)
        self.mode = 'LIVE'  # or 'FILE'

    def draw_overlays(self, frame):
        # draw stats panel
        stats = self.stats.current_stats()
        cv2.putText(frame, f"Shots: {stats['Attempts']}", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
        cv2.putText(frame, f"FG%: {stats['FG%']:.1f}", (10,60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
        return frame

    def run(self):
        # Main loop
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            detections = self.detector.detect(frame)
            tracks = self.tracker.update(detections)
            # TODO: integrate stats updates
            frame = self.draw_overlays(frame)
            cv2.imshow('Basketball Tracker', frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('c'):
                # calibration mode
                pass
        self.cap.release()
        cv2.destroyAllWindows()