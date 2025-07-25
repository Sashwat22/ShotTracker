from collections import deque
import numpy as np
import math

class ShotDetector:
    def __init__(self, hoop_y_threshold_factor=0.6, trajectory_frames=30, min_ball_confidence=0.4, min_hoop_confidence=0.25, nominal_fps=30):
        self.ball_positions_all_time = deque(maxlen=trajectory_frames) # For trajectory analysis, increased to 30
        self.current_shot_trajectory = [] # Store (center_x, center_y, frame_count) for current shot
        self.hoop_bbox = None
        self.hoop_center = None
        
        self.shot_in_progress = False
        self.ball_was_above_hoop = False
        self.frames_since_last_detection = 0 # To reset if ball/hoop not seen for a while

        self.shots_made = 0
        self.shots_attempted = 0
        
        # More forgiving threshold factors
        self.hoop_y_threshold_factor = hoop_y_threshold_factor  
        self.min_ball_confidence = min_ball_confidence  # Lower confidence threshold for ball
        self.min_hoop_confidence = min_hoop_confidence  # Lower confidence threshold for hoop

        self.frame_counter = 0
        self.last_arc_angle = None
        self.current_ball_speed_inst = None
        self.last_shot_avg_speed = None
        self.current_hoop_distance = None
        self.nominal_fps = nominal_fps

        # For advanced shot detection
        self.ball_up = False
        self.ball_down = False
        self.ball_up_frame = 0
        self.ball_down_frame = 0
        self.previous_shot_outcome = None
        
        # Additional variables for more robust detection
        self.hoop_position_buffer = deque(maxlen=10)  # Store recent hoop positions
        self.detection_cooldown = 0  # Prevent rapid re-detection
        
        print("Shot detector initialized")

    def _get_bbox_center(self, bbox):
        if bbox is None:
            return None
        x1, y1, x2, y2 = bbox
        return (int((x1 + x2) / 2), int((y1 + y2) / 2))
        
    def _get_stable_hoop_position(self):
        """Get a stable hoop position by averaging recent detections"""
        if not self.hoop_position_buffer:
            return self.hoop_bbox, self.hoop_center
            
        # Average the hoop positions
        avg_x1 = sum(bbox[0] for bbox in self.hoop_position_buffer) / len(self.hoop_position_buffer)
        avg_y1 = sum(bbox[1] for bbox in self.hoop_position_buffer) / len(self.hoop_position_buffer)
        avg_x2 = sum(bbox[2] for bbox in self.hoop_position_buffer) / len(self.hoop_position_buffer)
        avg_y2 = sum(bbox[3] for bbox in self.hoop_position_buffer) / len(self.hoop_position_buffer)
        
        avg_bbox = (int(avg_x1), int(avg_y1), int(avg_x2), int(avg_y2))
        avg_center = self._get_bbox_center(avg_bbox)
        
        return avg_bbox, avg_center

    def update(self, ball_bbox, hoop_bbox, current_frame_count):
        self.frame_counter = current_frame_count
        ball_center = self._get_bbox_center(ball_bbox)
        
        if self.detection_cooldown > 0:
            self.detection_cooldown -= 1
        
        # Stable hoop tracking
        if hoop_bbox:
            self.hoop_bbox = hoop_bbox
            self.hoop_center = self._get_bbox_center(hoop_bbox)
            self.hoop_position_buffer.append(hoop_bbox)
        else:
            # If hoop is lost but we have recent positions, use the average
            if len(self.hoop_position_buffer) > 0:
                self.hoop_bbox, self.hoop_center = self._get_stable_hoop_position()
            else:
                # If hoop is lost for too many frames, reset some state
                if self.hoop_bbox:  # if it was previously detected
                    self.frames_since_last_detection += 1
                    if self.frames_since_last_detection > 30:  # Increased threshold
                        self.hoop_bbox = None
                        self.hoop_center = None
                        self._reset_shot_state(reset_angle=True)
                        self.current_hoop_distance = None  # Hoop lost
                        return "NO_DETECTION", (self.shots_made, self.shots_attempted), self.last_arc_angle, self.current_ball_speed_inst, self.last_shot_avg_speed, self.current_hoop_distance, self.previous_shot_outcome

        self.frames_since_last_detection = 0

        if ball_center and self.hoop_center:
            # Always add to the general trajectory deque for instantaneous speed and arc fitting
            self.ball_positions_all_time.append((ball_center[0], ball_center[1], self.frame_counter))
            
            # If a shot is in progress, add to its specific trajectory
            if self.shot_in_progress:
                self.current_shot_trajectory.append((ball_center[0], ball_center[1], self.frame_counter))
            
            self.current_hoop_distance = np.sqrt((ball_center[0] - self.hoop_center[0])**2 + (ball_center[1] - self.hoop_center[1])**2)

            if len(self.ball_positions_all_time) >= 2:
                prev_pos = self.ball_positions_all_time[-2]
                curr_pos = self.ball_positions_all_time[-1]
                pixel_distance = np.sqrt((curr_pos[0] - prev_pos[0])**2 + (curr_pos[1] - prev_pos[1])**2)
                time_interval = 1.0 / self.nominal_fps 
                self.current_ball_speed_inst = pixel_distance / time_interval
            else:
                self.current_ball_speed_inst = None

            ball_cx, ball_cy = ball_center
            hoop_cx, hoop_cy = self.hoop_center
            hoop_x1, hoop_y1, hoop_x2, hoop_y2 = self.hoop_bbox
            hoop_width = hoop_x2 - hoop_x1
            hoop_height = hoop_y2 - hoop_y1

            # Define rim height and upper area for shot detection
            rim_height = hoop_y1 + hoop_height * 0.5
            
            # More generous upper zone
            upper_zone_y = hoop_y1 - hoop_height * 1.2  # Even more space above hoop

            # Detect ball in upper zone (above hoop) with more generous boundaries
            if not self.ball_up and ball_cy < upper_zone_y:
                # Ball must be within reasonable x-range of hoop (expanded range)
                if hoop_x1 - hoop_width * 2.0 < ball_cx < hoop_x2 + hoop_width * 2.0:
                    self.ball_up = True
                    self.ball_up_frame = self.frame_counter
                    self.shot_in_progress = True
                    self.ball_was_above_hoop = True
                    self.current_shot_trajectory = [(ball_cx, ball_cy, self.frame_counter)]
                    print(f"Ball detected above hoop at y={ball_cy}, upper_zone={upper_zone_y}")

            # Detect ball in lower zone (below hoop) with more generous boundaries
            if self.ball_up and not self.ball_down and ball_cy > hoop_y2:
                # Ball must be within reasonable x-range of hoop (expanded range)
                if hoop_x1 - hoop_width * 1.5 < ball_cx < hoop_x2 + hoop_width * 1.5:
                    self.ball_down = True
                    self.ball_down_frame = self.frame_counter
                    print(f"Ball detected below hoop at y={ball_cy}, hoop_y2={hoop_y2}")

            # Shot attempt detection and scoring
            if self.ball_up and self.ball_down and self.ball_up_frame < self.ball_down_frame and self.detection_cooldown == 0:
                # This is a shot attempt - calculate if it was made
                self.shots_attempted += 1
                
                # Determine if the shot went in
                made = self._score_shot()
                
                if made:
                    self.shots_made += 1
                    self.previous_shot_outcome = "MADE"
                else:
                    self.previous_shot_outcome = "MISSED"
                
                # Calculate stats
                self.last_arc_angle = self._calculate_arc_angle(list(self.ball_positions_all_time))
                self.last_shot_avg_speed = self._calculate_average_speed(self.current_shot_trajectory)
                
                # Reset shot detection
                self._reset_shot_state()
                
                # Set cooldown to prevent immediate re-detection
                self.detection_cooldown = 15
                
                return self.previous_shot_outcome, (self.shots_made, self.shots_attempted), self.last_arc_angle, self.current_ball_speed_inst, self.last_shot_avg_speed, self.current_hoop_distance, self.previous_shot_outcome

            # Return ongoing progress
            return "IN_PROGRESS", (self.shots_made, self.shots_attempted), self.last_arc_angle, self.current_ball_speed_inst, self.last_shot_avg_speed, self.current_hoop_distance, self.previous_shot_outcome
        
        elif not ball_center and self.hoop_center:
            self.current_ball_speed_inst = None
            self.current_hoop_distance = None
            
            # If ball is lost during active shot tracking, potentially count as missed
            if self.shot_in_progress and self.detection_cooldown == 0:
                self.frames_since_last_detection += 1
                if self.frames_since_last_detection > 15:  # Increased from 10
                    if self.ball_up and not self.ball_down:  # Ball went up but never came down
                        self.shots_attempted += 1
                        self.previous_shot_outcome = "MISSED"
                        self.last_arc_angle = self._calculate_arc_angle(list(self.ball_positions_all_time))
                        self.last_shot_avg_speed = self._calculate_average_speed(self.current_shot_trajectory)
                        self._reset_shot_state()
                        
                        # Set cooldown to prevent immediate re-detection
                        self.detection_cooldown = 15
                        
                        return "MISSED", (self.shots_made, self.shots_attempted), self.last_arc_angle, self.current_ball_speed_inst, self.last_shot_avg_speed, self.current_hoop_distance, self.previous_shot_outcome
            
            return "NO_ACTION", (self.shots_made, self.shots_attempted), self.last_arc_angle, self.current_ball_speed_inst, self.last_shot_avg_speed, self.current_hoop_distance, self.previous_shot_outcome
        
        elif ball_center and not self.hoop_center:
            self.current_hoop_distance = None
            
            # Always add to the trajectory for tracking, even without hoop
            self.ball_positions_all_time.append((ball_center[0], ball_center[1], self.frame_counter))
            
            # Still track ball position even if hoop is lost
            if len(self.ball_positions_all_time) >= 2:
                prev_pos = self.ball_positions_all_time[-2]
                curr_pos = self.ball_positions_all_time[-1]
                pixel_distance = np.sqrt((curr_pos[0] - prev_pos[0])**2 + (curr_pos[1] - prev_pos[1])**2)
                time_interval = 1.0 / self.nominal_fps
                self.current_ball_speed_inst = pixel_distance / time_interval
            else:
                self.current_ball_speed_inst = None
            
            return "NO_ACTION", (self.shots_made, self.shots_attempted), self.last_arc_angle, self.current_ball_speed_inst, self.last_shot_avg_speed, self.current_hoop_distance, self.previous_shot_outcome
        
        else:
            self.current_ball_speed_inst = None
            self.current_hoop_distance = None
            return "NO_ACTION", (self.shots_made, self.shots_attempted), self.last_arc_angle, self.current_ball_speed_inst, self.last_shot_avg_speed, self.current_hoop_distance, self.previous_shot_outcome

    def _score_shot(self):
        """Determine if a shot went through the hoop based on trajectory"""
        if not self.hoop_bbox or len(self.current_shot_trajectory) < 3:
            return False
            
        # Get hoop dimensions
        hoop_x1, hoop_y1, hoop_x2, hoop_y2 = self.hoop_bbox
        hoop_width = hoop_x2 - hoop_x1
        
        # Calculate the rim height (middle of the hoop)
        rim_height = hoop_y1 + (hoop_y2 - hoop_y1) * 0.5
        
        # Find points above and below rim for trajectory analysis
        points_above_rim = []
        points_below_rim = []
        
        # Collect points above and below rim
        for x, y, frame in self.current_shot_trajectory:
            if y < rim_height:
                points_above_rim.append((x, y))
            else:
                points_below_rim.append((x, y))
        
        # Need points both above and below rim for analysis
        if not points_above_rim or not points_below_rim:
            return False
            
        # Get the closest point above rim and below rim
        above_point = max(points_above_rim, key=lambda p: p[1])  # closest to rim from above
        below_point = min(points_below_rim, key=lambda p: p[1])  # closest to rim from below
        
        # Only consider shots where there's a clear trajectory through the rim area
        if above_point and below_point:
            # Create a line between these two points to predict path through rim
            x1, y1 = above_point
            x2, y2 = below_point
            
            # Calculate where the ball would pass through the rim height
            # Avoid division by zero if points are directly above/below each other
            if y2 - y1 != 0:
                t = (rim_height - y1) / (y2 - y1)
                intersection_x = x1 + t * (x2 - x1)
                
                # Check if this intersection point is within the hoop bounds
                # More forgiving intersection test (0.7 instead of 0.5)
                rim_x1 = self.hoop_center[0] - 0.7 * hoop_width
                rim_x2 = self.hoop_center[0] + 0.7 * hoop_width
                
                if rim_x1 < intersection_x < rim_x2:
                    print(f"SHOT MADE! Intersection at x={intersection_x}, rim bounds: {rim_x1}-{rim_x2}")
                    return True
                else:
                    print(f"SHOT MISSED! Intersection at x={intersection_x}, rim bounds: {rim_x1}-{rim_x2}")
        
        return False

    def _reset_shot_state(self, reset_angle=False):
        self.shot_in_progress = False
        self.ball_was_above_hoop = False
        self.ball_positions_all_time.clear()
        self.current_shot_trajectory = []
        self.frames_since_last_detection = 0
        
        # Reset ball position detection vars
        self.ball_up = False
        self.ball_down = False
        
        if reset_angle:
            self.last_arc_angle = None
            self.last_shot_avg_speed = None

    def _calculate_average_speed(self, trajectory):
        if not trajectory or len(trajectory) < 2:
            return None
        
        total_pixel_distance = 0
        for i in range(len(trajectory) - 1):
            p1 = trajectory[i]
            p2 = trajectory[i+1]
            total_pixel_distance += np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
            
        total_time_seconds = (len(trajectory) -1) * (1.0 / self.nominal_fps)
        
        if total_time_seconds == 0:
            return None
            
        average_speed = total_pixel_distance / total_time_seconds
        return average_speed

    def _calculate_arc_angle(self, trajectory):
        if not trajectory or len(trajectory) < 3:
            return None

        # Extract x and y coordinates
        x_coords = np.array([pos[0] for pos in trajectory])
        y_coords = np.array([pos[1] for pos in trajectory])

        # Check for degenerate cases
        if len(np.unique(x_coords)) < 2:
            return None

        try:
            # Fit a 2nd degree polynomial
            coeffs = np.polyfit(x_coords, y_coords, 2)
        except (np.linalg.LinAlgError, ValueError):
            return None
        
        # Derivative: dy/dx = 2ax + b
        slope = 2 * coeffs[0] * x_coords[0] + coeffs[1]
        
        angle_rad = np.arctan(slope)
        angle_deg = np.degrees(angle_rad)
        
        # Adjusting angle: In image coordinates, y increases downwards
        # A typical upward shot would have a negative slope
        return -angle_deg

    def get_stats(self):
        return self.shots_made, self.shots_attempted 

    def full_reset(self):
        """Completely reset the shot detector state"""
        self.ball_positions_all_time.clear()
        self.current_shot_trajectory.clear()
        self.hoop_bbox = None
        self.hoop_center = None
        
        self.shot_in_progress = False
        self.ball_was_above_hoop = False
        self.frames_since_last_detection = 0
        
        self.shots_made = 0
        self.shots_attempted = 0
        
        self.frame_counter = 0
        self.last_arc_angle = None
        self.current_ball_speed_inst = None
        self.last_shot_avg_speed = None
        self.current_hoop_distance = None
        
        self.ball_up = False
        self.ball_down = False
        self.ball_up_frame = 0
        self.ball_down_frame = 0
        self.previous_shot_outcome = None
        
        self.hoop_position_buffer.clear()
        self.detection_cooldown = 0
        
        print("Shot detector fully reset") 