import cv2
import numpy as np

class BallTracker:
    def __init__(self, max_trail_length=15):
        # Ball trajectory tracking
        self.positions = []
        self.max_trail_length = max_trail_length
        self.show_trail = True
        self.trail_color = (0, 0, 255)  # Red color for trail (BGR)
    
    def add_position(self, ball_center):
        """Add a new ball position to the trail"""
        if ball_center:
            # Add current position to trail with full intensity
            self.positions.append((ball_center, 1.0))
            
            # Keep only the last N positions
            if len(self.positions) > self.max_trail_length:
                self.positions = self.positions[-self.max_trail_length:]
                
    def clear_trail(self):
        """Clear the ball trail and reset tracker state"""
        self.positions = []
        # Make sure the trail is visible when starting a new video
        self.show_trail = True
            
    def toggle_trail(self):
        """Toggle the display of the ball trail"""
        self.show_trail = not self.show_trail
        return self.show_trail
            
    def draw_trail(self, frame):
        """Draw the ball trail on the given frame"""
        if not self.show_trail or not self.positions:
            return frame
            
        annotated_frame = frame.copy()
        
        # Draw each trail position
        for i, (pos, intensity) in enumerate(self.positions):
            # Fading intensity - newer positions are more intense
            fade = intensity * (i+1) / len(self.positions)
            
            # Size increases with recency
            size = int(5 + (8 * fade))
            
            # Red trail with fading transparency
            alpha = int(180 * fade)
            
            # Create a separate overlay for each trail dot
            overlay = annotated_frame.copy()
            cv2.circle(overlay, pos, size, self.trail_color, -1)
            cv2.addWeighted(overlay, alpha/255, annotated_frame, 1 - alpha/255, 0, annotated_frame)
                
        return annotated_frame 