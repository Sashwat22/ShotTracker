import cv2
import os
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtWidgets import QLabel, QSlider, QPushButton, QVBoxLayout, QHBoxLayout, QStyle
from PyQt5.QtGui import QImage, QPixmap

class VideoPlayer:
    def __init__(self, parent):
        self.parent = parent
        self.video_path = None
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.process_frame)
        self.is_paused = False
        self.current_frame_num = 0
        self.total_frames = 0
        
        # Setup UI components
        self.video_layout = QVBoxLayout()
        
        # Video display label
        self.video_label = QLabel("Please select a video folder to start\nor configure settings.")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setMinimumSize(720, 480)
        self.video_label.setStyleSheet("border: 1px solid #333333; border-radius: 4px; padding: 5px;")
        self.video_layout.addWidget(self.video_label)

        # Video Progress Bar
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setRange(0, 100)
        self.progress_slider.setValue(0)
        self.progress_slider.setEnabled(False)
        self.progress_slider.setTracking(False)
        self.progress_slider.sliderMoved.connect(self.seek_position)
        self.video_layout.addWidget(self.progress_slider)
        
        # Control buttons
        control_layout = QHBoxLayout()
        
        self.btn_play_pause = QPushButton("Play")
        self.btn_play_pause.setIcon(parent.style().standardIcon(QStyle.SP_MediaPlay))
        self.btn_play_pause.clicked.connect(self.toggle_play_pause)
        self.btn_play_pause.setEnabled(False)
        control_layout.addWidget(self.btn_play_pause)
        
        self.btn_toggle_trail = QPushButton("Toggle Ball Trail")
        self.btn_toggle_trail.clicked.connect(self.toggle_trail)
        control_layout.addWidget(self.btn_toggle_trail)
        
        self.video_layout.addLayout(control_layout)
        
    def get_layout(self):
        """Return the video player layout"""
        return self.video_layout
        
    def toggle_trail(self):
        """Toggle the display of the ball trail"""
        if hasattr(self.parent, 'ball_tracker'):
            is_showing = self.parent.ball_tracker.toggle_trail()
            self.btn_toggle_trail.setText("Hide Ball Trail" if is_showing else "Show Ball Trail")
        
    def load_video(self, video_file_path):
        """Load a video file for playback"""
        self.stop_video()
        
        # Reset counters and state
        self.current_frame_num = 0
        self.total_frames = 0
        
        self.video_path = video_file_path
        if not self.video_path or not os.path.exists(self.video_path):
            self.video_label.setText(f"Error: File not found\n{self.video_path}")
            self.video_label.setStyleSheet("border: 1px solid #333333; border-radius: 4px; padding: 5px; color: #FF5555;")
            self.btn_play_pause.setEnabled(False)
            self.progress_slider.setEnabled(False)
            return False
            
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            self.video_label.setText(f"Error loading video: {self.video_path}")
            self.video_label.setStyleSheet("border: 1px solid #333333; border-radius: 4px; padding: 5px; color: #FF5555;")
            self.btn_play_pause.setEnabled(False)
            self.progress_slider.setEnabled(False)
            return False
            
        # Video loaded successfully
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.progress_slider.setRange(0, self.total_frames if self.total_frames > 0 else 100)
        self.progress_slider.setValue(0)
        self.progress_slider.setEnabled(self.total_frames > 0)
        
        self.current_frame_num = 0
        self.is_paused = False
        self.btn_play_pause.setText("Pause")
        self.btn_play_pause.setIcon(self.parent.style().standardIcon(QStyle.SP_MediaPause))
        self.btn_play_pause.setEnabled(True)
        self.video_label.setStyleSheet("background-color: black; border: 1px solid #333333;")
        
        # Start playing
        self.timer.start(30)  # ~30fps
        return True
        
    def process_frame(self):
        """Process and display the next video frame"""
        if self.parent.frame_processor:
            self.parent.frame_processor.process_next_frame()
        
    def display_frame(self, frame):
        """Display a processed frame"""
        if frame is None:
            return
            
        # Simple dark border around the frame
        border_size = 2
        bordered_frame = cv2.copyMakeBorder(
            frame, 
            border_size, border_size, border_size, border_size, 
            cv2.BORDER_CONSTANT, 
            value=(30, 30, 30)  # Dark gray border
        )
        
        rgb_image = cv2.cvtColor(bordered_frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(qt_image))
        
    def toggle_play_pause(self):
        """Toggle between playing and pausing the video"""
        if not self.cap or not self.cap.isOpened():
            return

        if self.is_paused:
            # Check if video ended and user wants to replay
            current_pos_frames = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            if current_pos_frames >= self.total_frames and self.total_frames > 0:
                self.reset_video()
            
            self.timer.start(30)
            self.btn_play_pause.setText("Pause")
            self.btn_play_pause.setIcon(self.parent.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.timer.stop()
            self.btn_play_pause.setText("Play")
            self.btn_play_pause.setIcon(self.parent.style().standardIcon(QStyle.SP_MediaPlay))
            
        self.is_paused = not self.is_paused
        
    def stop_video(self):
        """Stop video playback and release resources"""
        if self.timer.isActive():
            self.timer.stop()
        if self.cap:
            self.cap.release()
            self.cap = None
        self.is_paused = True
        self.btn_play_pause.setText("Play")
        self.btn_play_pause.setIcon(self.parent.style().standardIcon(QStyle.SP_MediaPlay))
        self.btn_play_pause.setEnabled(False)
        self.progress_slider.setValue(0)
        self.progress_slider.setEnabled(False)
        
    def reset_video(self):
        """Reset video to beginning"""
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.current_frame_num = 0
            self.progress_slider.setValue(0)
            
            # Reset other components
            if hasattr(self.parent, 'shot_detector'):
                self.parent.shot_detector = self.parent.create_shot_detector()
            if hasattr(self.parent, 'ball_tracker'):
                self.parent.ball_tracker.clear_trail()
            if hasattr(self.parent, 'stats_display'):
                self.parent.stats_display.reset_stats()
                
    def get_frame(self):
        """Get the next frame from the video"""
        if not self.cap or not self.cap.isOpened():
            return None, False
            
        ret, frame = self.cap.read()
        if not ret:
            self.handle_video_end()
            return None, False
            
        self.current_frame_num += 1
        # Update progress slider if not currently being pressed by user
        if not self.progress_slider.isSliderDown():
            current_pos_frames = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            self.progress_slider.setValue(current_pos_frames)
            
        return frame, True
        
    def handle_video_end(self):
        """Handle actions when video playback ends"""
        self.timer.stop()
        if self.cap:
            self.cap.release()
            self.cap = None
            
        self.btn_play_pause.setText("Play")
        self.btn_play_pause.setIcon(self.parent.style().standardIcon(QStyle.SP_MediaPlay))
        self.btn_play_pause.setEnabled(False)
        
        if self.total_frames > 0:
            self.progress_slider.setValue(self.total_frames)
            
        if hasattr(self.parent, 'stats_display'):
            self.parent.stats_display.set_status("Video Ended")
            self.parent.stats_display.set_result("SESSION COMPLETE")
            
    def seek_position(self, position):
        """Seek to a specific position in the video"""
        if self.cap and self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, position)
            # Reset tracking state when seeking
            if hasattr(self.parent, 'shot_detector'):
                self.parent.shot_detector = self.parent.create_shot_detector()
            if hasattr(self.parent, 'ball_tracker'):
                self.parent.ball_tracker.clear_trail()
            
            # Read the frame at the new position
            success, frame = self.cap.read()
            if success and hasattr(self.parent, 'frame_processor'):
                self.parent.frame_processor.process_frame(frame) 