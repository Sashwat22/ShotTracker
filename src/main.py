import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, 
                             QPushButton, QFileDialog, QHBoxLayout, QGroupBox, 
                             QSizePolicy, QStyle, QScrollArea, QGridLayout, QSlider, QFrame, QDialog, QListWidget, QListWidgetItem)
from PyQt5.QtGui import QImage, QPixmap, QPainter, QColor, QPen, QFont, QIcon, QFontDatabase
from PyQt5.QtCore import Qt, QTimer, QPoint, QRectF
import cv2
import numpy as np
from ultralytics import YOLO

# Import our modules
from ui import VideoPlayer, StatsDisplay, VideoBrowser, ConfigDialog
from models import BallTracker, YOLODetector
from processors import FrameProcessor, ShotDetector

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Basketball Shot Analysis")
        self.setGeometry(100, 100, 1350, 800)

        # Try to load custom fonts
        self.load_custom_fonts()

        # Apply a clean, minimal dark theme
        self.apply_style_sheet()

        # Initialize configuration
        self.video_folder_path = "data/videos"
        self.model_path = "best.pt"
        
        # Create main components
        self.yolo_detector = YOLODetector(self.model_path)
        self.shot_detector = self.create_shot_detector()
        self.ball_tracker = BallTracker()
        
        # Setup UI
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        # Create video player
        self.video_player = VideoPlayer(self)
        
        # Create title for video area
        video_title = QLabel("BASKETBALL SHOT ANALYSIS")
        video_title.setFont(QFont("Roboto Condensed", 22) if "Roboto Condensed" in QFontDatabase().families() else QFont("Arial", 22, QFont.Bold))
        video_title.setAlignment(Qt.AlignCenter)
        video_title.setStyleSheet("color: #FFFFFF; margin-bottom: 15px; font-weight: bold;")
        
        # Add title to the top of video layout
        video_layout = QVBoxLayout()
        video_layout.addWidget(video_title)
        video_layout.addLayout(self.video_player.get_layout())
        
        # Add to main layout
        self.main_layout.addLayout(video_layout, 2)

        # Create right panel for controls and stats
        self.right_panel_widget = QWidget()
        self.right_panel_layout = QVBoxLayout(self.right_panel_widget)
        self.right_panel_layout.setContentsMargins(15, 15, 15, 15)
        
        # Create video browser
        self.video_browser = VideoBrowser(self)
        self.right_panel_layout.addWidget(self.video_browser.get_group())
        
        # Create statistics display
        self.stats_display = StatsDisplay(self)
        self.right_panel_layout.addWidget(self.stats_display.get_group())
        
        # Add spacer at the bottom
        self.right_panel_layout.addStretch()

        # Create scroll area for the right panel
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setWidget(self.right_panel_widget)
        self.main_layout.addWidget(self.scroll_area, 1)
        
        # Set up frame processor
        self.frame_processor = FrameProcessor(self)
        self.frame_processor.set_components(
            self.video_player, 
            self.shot_detector, 
            self.yolo_detector, 
            self.ball_tracker, 
            self.stats_display
        )

    def load_custom_fonts(self):
        """Load sports-style fonts if available"""
        sports_fonts = ["Roboto", "Roboto Condensed", "Oswald"]
        font_db = QFontDatabase()
        
        # Font directories to check
        font_dirs = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "../fonts"),
            "fonts",
            "/Library/Fonts",
            "C:\\Windows\\Fonts"
        ]
        
        for font_dir in font_dirs:
            if os.path.exists(font_dir):
                for font_file in os.listdir(font_dir):
                    if font_file.lower().endswith(('.ttf', '.otf')):
                        font_path = os.path.join(font_dir, font_file)
                        font_db.addApplicationFont(font_path)

    def apply_style_sheet(self):
        """Apply a clean, minimal dark theme to the application"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212; /* Very dark gray - Google Material dark theme base */
            }
            QGroupBox {
                background-color: #1E1E1E; /* Slightly lighter background for groups */
                border: 1px solid #333333;
                border-radius: 6px;
                margin-top: 1.5ex;
                color: #FFFFFF;
                font-weight: bold;
                font-size: 14px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 8px;
                background-color: #1E1E1E;
            }
            QLabel {
                color: #FFFFFF; /* White text for better readability */
                background-color: transparent;
                font-size: 14px; /* Larger font */
            }
            QPushButton {
                background-color: #2C2C2C; /* Subtle button background */
                color: #FFFFFF;
                border: none;
                padding: 12px; /* Larger padding */
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px; /* Larger font */
            }
            QPushButton:hover {
                background-color: #3F3F3F; /* Lighten on hover */
            }
            QPushButton:pressed {
                background-color: #555555; /* Even lighter when pressed */
            }
            QPushButton:disabled {
                background-color: #1A1A1A;
                color: #5A5A5A;
            }
            QListWidget {
                background-color: #1E1E1E;
                color: #FFFFFF;
                border: 1px solid #333333;
                border-radius: 4px;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 8px; /* More padding for better touch targets */
            }
            QListWidget::item:hover {
                background-color: #2A2A2A;
            }
            QListWidget::item:selected {
                background-color: #424242; /* Material design selected item color */
                color: white;
            }
            QSlider::groove:horizontal {
                border: none;
                height: 8px;
                background: #333333;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #AAAAAA; /* Light gray handle */
                border: none;
                width: 18px;
                height: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: #CCCCCC; /* Lighter on hover */
            }
            QLineEdit {
                background-color: #2A2A2A;
                color: white;
                border: 1px solid #333333;
                padding: 8px;
                border-radius: 4px;
                font-size: 14px;
            }
            QScrollArea {
                border: none;
            }
        """)

    def create_shot_detector(self):
        """Create a new instance of the shot detector"""
        return ShotDetector()

    def load_video(self, video_path):
        """Load a video file and reset the app state"""
        # Stop any existing video
        self.video_player.stop_video()
        
        # Reset the shot detector completely or create a new one
        if hasattr(self, 'shot_detector') and self.shot_detector:
            self.shot_detector.full_reset()
        else:
            self.shot_detector = self.create_shot_detector()
        
        # Reset ball tracker to clear any trails
        self.ball_tracker.clear_trail()
        
        # Reset statistics display completely
        self.stats_display.reset_stats()
        
        # Update frame processor with the new shot detector
        self.frame_processor.set_components(
            self.video_player, 
            self.shot_detector, 
            self.yolo_detector, 
            self.ball_tracker, 
            self.stats_display
        )
        
        # Load video
        if self.video_player.load_video(video_path):
            self.stats_display.set_status("Video loaded, playing...")
            print(f"Video loaded: {video_path}")
            print("Shot detector and statistics reset")
        else:
            self.stats_display.set_status("Error loading video")
            
    def open_settings_dialog(self):
        """Open the configuration dialog"""
        dialog = ConfigDialog(
            self.video_browser.get_video_folder_path(), 
            self.yolo_detector.model_path, 
            self
        )
        
        if dialog.exec_() == QDialog.Accepted:
            new_video_path, new_model_path = dialog.get_paths()
            
            # Update video folder path
            if new_video_path != self.video_browser.get_video_folder_path():
                self.video_browser.set_video_folder_path(new_video_path)
            
            # Update model if changed
            if new_model_path != self.yolo_detector.model_path:
                # Stop video playback
                self.video_player.stop_video()
                
                # Try to load new model
                success, message = self.yolo_detector.load_model(new_model_path)
                
                if success:
                    self.stats_display.set_status("New model loaded. Select video.")
                else:
                    self.stats_display.set_status("Error loading model.")
                    self.stats_display.set_result("MODEL ERROR", is_made=False)

def main():
    # Suppress NSOpenPanel warning on macOS
    if sys.platform == 'darwin':
        os.environ['QT_MAC_WANTS_LAYER'] = '1'

    app = QApplication(sys.argv)
    main_app = MainApp()
    main_app.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
