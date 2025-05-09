import cv2
import numpy as np

class FrameProcessor:
    def __init__(self, parent):
        self.parent = parent
        # References to components
        self.video_player = None
        self.shot_detector = None
        self.yolo_detector = None  
        self.ball_tracker = None
        self.stats_display = None
        
    def set_components(self, video_player, shot_detector, yolo_detector, ball_tracker, stats_display):
        """Set references to all components needed for processing"""
        self.video_player = video_player
        self.shot_detector = shot_detector
        self.yolo_detector = yolo_detector
        self.ball_tracker = ball_tracker
        self.stats_display = stats_display
        
        # Reset any cached state when components are changed
        self.reset_state()
        
    def reset_state(self):
        """Reset the processor state"""
        # Clear any cached state in the frame processor
        if self.stats_display:
            # Make sure no flashes are active
            self.stats_display.shot_made_flash = 0
            self.stats_display.shot_miss_flash = 0
            self.stats_display.previous_shot_outcome = None
            
        print("Frame processor state reset")
        
    def process_next_frame(self):
        """Process the next frame from the video"""
        if not self.video_player or not self.shot_detector or not self.yolo_detector or not self.ball_tracker:
            return
            
        # Get the next frame
        frame, success = self.video_player.get_frame()
        if not success or frame is None:
            return
            
        # Process the frame
        self.process_frame(frame)
        
    def process_frame(self, frame):
        """Process a single frame"""
        if frame is None:
            return
            
        try:
            # Run YOLO detection
            ball_bbox, hoop_bbox = self.yolo_detector.detect(frame)
            
            # Get current frame number
            current_frame_num = self.video_player.current_frame_num
            
            # Process detection with shot detector
            shot_status, stats, arc_angle, inst_speed, avg_speed, hoop_dist, shot_outcome = (
                self.shot_detector.update(
                    ball_bbox[:4] if ball_bbox else None, 
                    hoop_bbox[:4] if hoop_bbox else None, 
                    current_frame_num
                )
            )
            
            # Update statistics display
            self.stats_display.update_stats(
                stats=stats,
                arc_angle=arc_angle,
                inst_speed=inst_speed,
                avg_speed=avg_speed,
                hoop_dist=hoop_dist
            )
            
            if shot_status == "PROCESSING":
                self.stats_display.set_status("Processing...")
            
            # Check for shot results and update UI
            if shot_status == "MADE" or shot_outcome == "MADE":
                self.stats_display.set_result("SHOT MADE!", is_made=True)
                # Force set flash to ensure visual feedback
                self.stats_display.shot_made_flash = self.stats_display.shot_made_flash_duration
                self.stats_display.shot_miss_flash = 0  # Ensure only one flash shows
                print("Shot MADE detected!")  # Debug output
            elif shot_status == "MISSED" or shot_outcome == "MISSED":
                self.stats_display.set_result("SHOT MISSED", is_made=False)
                # Force set flash to ensure visual feedback
                self.stats_display.shot_miss_flash = self.stats_display.shot_miss_flash_duration
                self.stats_display.shot_made_flash = 0  # Ensure only one flash shows
                print("Shot MISSED detected!")  # Debug output
                
            # Draw ball and hoop on the frame
            annotated_frame = self.yolo_detector.draw_detections(frame, ball_bbox, hoop_bbox)
            
            # Add ball trail
            if ball_bbox:
                ball_x1, ball_y1, ball_x2, ball_y2 = ball_bbox[:4]
                ball_center = ((ball_x1 + ball_x2) // 2, (ball_y1 + ball_y2) // 2)
                self.ball_tracker.add_position(ball_center)
            
            # Draw ball trail
            annotated_frame = self.ball_tracker.draw_trail(annotated_frame)
            
            # Apply flash effect for shot outcomes
            flash_type, intensity = self.stats_display.get_flash_status()
            if flash_type == "MADE":
                # Green flash for made shots
                overlay = np.zeros_like(annotated_frame)
                overlay[:] = (0, 255, 0)  # Pure green overlay
                alpha = 0.3 * (intensity / self.stats_display.shot_made_flash_duration)  # Fade out effect
                annotated_frame = cv2.addWeighted(overlay, alpha, annotated_frame, 1-alpha, 0)
                
                # Also add "MADE" text
                cv2.putText(annotated_frame, "MADE!", 
                           (annotated_frame.shape[1]//2 - 100, 100), 
                           cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 5)
                
            elif flash_type == "MISSED":
                # Red flash for missed shots
                overlay = np.zeros_like(annotated_frame)
                overlay[:] = (0, 0, 255)  # Pure red overlay
                alpha = 0.3 * (intensity / self.stats_display.shot_miss_flash_duration)  # Fade out effect
                annotated_frame = cv2.addWeighted(overlay, alpha, annotated_frame, 1-alpha, 0)
                
                # Also add "MISSED" text
                cv2.putText(annotated_frame, "MISSED", 
                           (annotated_frame.shape[1]//2 - 100, 100), 
                           cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 5)
            
            # Display the frame
            self.video_player.display_frame(annotated_frame)
            
        except Exception as e:
            print(f"Error processing frame: {e}")
            # Still display the original frame to prevent black screen
            self.video_player.display_frame(frame)
            self.stats_display.set_status(f"Processing error: {str(e)[:50]}") 