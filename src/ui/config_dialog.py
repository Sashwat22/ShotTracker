from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt

class ConfigDialog(QDialog):
    def __init__(self, current_video_path, current_model_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration")
        self.setModal(True)
        self.setMinimumWidth(500)

        self.current_video_path = current_video_path
        self.current_model_path = current_model_path

        layout = QVBoxLayout(self)

        # Video Path
        video_path_layout = QHBoxLayout()
        video_label = QLabel("Video Folder Path:")
        self.video_path_edit = QLineEdit(self.current_video_path)
        self.video_path_button = QPushButton("Browse...")
        self.video_path_button.clicked.connect(self.browse_video_folder)
        video_path_layout.addWidget(video_label)
        video_path_layout.addWidget(self.video_path_edit)
        video_path_layout.addWidget(self.video_path_button)
        layout.addLayout(video_path_layout)

        # Model Path
        model_path_layout = QHBoxLayout()
        model_label = QLabel("YOLO Model Path (.pt):")
        self.model_path_edit = QLineEdit(self.current_model_path)
        self.model_path_button = QPushButton("Browse...")
        self.model_path_button.clicked.connect(self.browse_model_file)
        model_path_layout.addWidget(model_label)
        model_path_layout.addWidget(self.model_path_edit)
        model_path_layout.addWidget(self.model_path_button)
        layout.addLayout(model_path_layout)

        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.accept) # QDialog.accept()
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject) # QDialog.reject()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

    def browse_video_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Video Folder", self.video_path_edit.text() or ".")
        if path:
            self.video_path_edit.setText(path)

    def browse_model_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select YOLO Model File", self.model_path_edit.text() or ".", "PyTorch Model Files (*.pt)")
        if path:
            self.model_path_edit.setText(path)

    def get_paths(self):
        return self.video_path_edit.text(), self.model_path_edit.text() 