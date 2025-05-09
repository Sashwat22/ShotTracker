import os
from PyQt5.QtWidgets import (QPushButton, QVBoxLayout, QHBoxLayout, QLabel, 
                             QListWidget, QListWidgetItem, QGroupBox, QStyle, QFileDialog)

class VideoBrowser:
    def __init__(self, parent):
        self.parent = parent
        self.video_folder_path = "data/videos"  # Default path
        self.current_video_files = []
        
        # Create controls group
        self.controls_group = QGroupBox("CONTROLS")
        self.controls_layout = self._create_controls_layout()
        self.controls_group.setLayout(self.controls_layout)
        
    def _create_controls_layout(self):
        """Create the controls layout"""
        controls_layout = QVBoxLayout()
        controls_layout.setSpacing(15)
        
        # Select video folder button
        self.btn_select_video = QPushButton("Select Video Folder")
        self.btn_select_video.setIcon(self.parent.style().standardIcon(QStyle.SP_DirOpenIcon))
        self.btn_select_video.clicked.connect(self.select_video_folder)
        self.btn_select_video.setFixedHeight(50)
        controls_layout.addWidget(self.btn_select_video)
        
        # Settings button
        self.btn_settings = QPushButton("Settings")
        self.btn_settings.setIcon(self.parent.style().standardIcon(QStyle.SP_FileDialogDetailedView))
        self.btn_settings.clicked.connect(self.open_settings_dialog)
        self.btn_settings.setFixedHeight(50)
        controls_layout.addWidget(self.btn_settings)
        
        # Video List
        controls_layout.addWidget(QLabel("Available Videos:"))
        self.video_files_list_widget = QListWidget()
        self.video_files_list_widget.itemDoubleClicked.connect(self.on_video_selected_from_list)
        self.video_files_list_widget.setEnabled(False)
        self.video_files_list_widget.setFixedHeight(150)
        controls_layout.addWidget(self.video_files_list_widget)
        
        return controls_layout
    
    def get_group(self):
        """Return the controls group widget"""
        return self.controls_group
        
    def select_video_folder(self):
        """Open a folder dialog to select video directory"""
        # Stop current video playback before opening dialog
        if hasattr(self.parent, 'video_player'):
            self.parent.video_player.stop_video()
            
        new_folder_path = QFileDialog.getExistingDirectory(self.parent, "Select Video Folder", self.video_folder_path)
        if new_folder_path:
            self.video_folder_path = new_folder_path
            self.populate_video_list()
            
    def populate_video_list(self):
        """Populate the list of available videos"""
        self.video_files_list_widget.clear()
        self.current_video_files = []
        
        if not self.video_folder_path or not os.path.isdir(self.video_folder_path):
            self.video_files_list_widget.addItem("No folder selected or folder not found.")
            self.video_files_list_widget.setEnabled(False)
            return

        try:
            videos = [f for f in os.listdir(self.video_folder_path) if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))]
            if videos:
                for video_file_name in sorted(videos):
                    self.video_files_list_widget.addItem(QListWidgetItem(video_file_name))
                    self.current_video_files.append(os.path.join(self.video_folder_path, video_file_name))
                self.video_files_list_widget.setEnabled(True)
            else:
                self.video_files_list_widget.addItem("No video files found in folder.")
                self.video_files_list_widget.setEnabled(False)
        except Exception as e:
            print(f"Error populating video list: {e}")
            self.video_files_list_widget.addItem("Error reading folder contents.")
            self.video_files_list_widget.setEnabled(False)
    
    def on_video_selected_from_list(self, item):
        """Handle video selection from the list"""
        selected_video_name = item.text()
        
        # Stop current video if playing
        if hasattr(self.parent, 'video_player'):
            self.parent.video_player.stop_video()

        full_video_path = os.path.join(self.video_folder_path, selected_video_name)
        if os.path.exists(full_video_path):
            self.parent.load_video(full_video_path)
        else:
            print(f"Error: Selected video file not found: {full_video_path}")
            if hasattr(self.parent, 'video_player'):
                self.parent.video_player.video_label.setText(f"Error: File not found\n{selected_video_name}")
                self.parent.video_player.video_label.setStyleSheet("border: 1px solid #333333; border-radius: 4px; padding: 5px; color: #FF5555;")
                
    def open_settings_dialog(self):
        """Open the settings dialog"""
        if hasattr(self.parent, 'open_settings_dialog'):
            self.parent.open_settings_dialog()
            
    def get_video_folder_path(self):
        """Return the current video folder path"""
        return self.video_folder_path
        
    def set_video_folder_path(self, path):
        """Set the video folder path and refresh the list"""
        if os.path.isdir(path):
            self.video_folder_path = path
            self.populate_video_list()
            return True
        return False 