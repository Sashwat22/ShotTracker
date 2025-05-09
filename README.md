# Basketball Shot Analysis

A Python application that analyzes basketball shots using computer vision and provides real-time statistics and feedback.

## Features

- Real-time detection of basketball and hoop using YOLO
- Shot tracking and trajectory analysis
- Statistics tracking (shots made/missed, launch angle, ball speed)
- Video playback controls with progress tracking
- Ball trajectory visualization
- Modern dark-themed UI with PyQt5

## Project Structure

The application has a modular structure:

```
src/
├── main.py                  # Main application entry point
├── models/                  # ML and tracking models
│   ├── __init__.py
│   ├── ball_tracker.py      # Ball trail tracking
│   └── yolo_detector.py     # YOLO object detection
├── processors/              # Data processors
│   ├── __init__.py
│   ├── frame_processor.py   # Video frame processing
│   └── shot_detector.py     # Shot detection and analysis
└── ui/                      # User interface components
    ├── __init__.py
    ├── config_dialog.py     # Configuration dialog
    ├── stats_display.py     # Statistics display
    ├── video_browser.py     # Video file browser
    └── video_player.py      # Video playback
```

## Requirements

- Python 3.8+
- PyQt5
- OpenCV (cv2)
- NumPy
- Ultralytics YOLO
- deep-sort-realtime
- scipy

## Setup

1. Clone the repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `data/videos` directory to store your basketball videos
4. Ensure you have a `best.pt` YOLO model file in the root directory (trained on basketball and hoop detection)

## Usage

1. Run the application:
   ```
   python -m src.main
   ```
2. Click "Select Video Folder" to browse for videos containing basketball shots
3. Double-click a video to start analysis
4. Use the playback controls to pause/play and navigate the video
5. Toggle the ball trail for trajectory visualization
6. View real-time statistics including:
   - Shot count (made/attempted)
   - Shot success rate
   - Launch angle
   - Ball speed
   - Distance to hoop

## Features

### Shot Detection
The application uses a robust algorithm to detect basketball shots by tracking:
- The ball's position relative to the hoop
- Upward and downward motion of the ball
- Trajectory patterns
- Ball position relative to the hoop rim

### Real-Time Analysis
While analyzing videos, the app provides immediate feedback on:
- Shot success or failure
- Shot arc angle
- Ball speed
- Current distance from ball to hoop

### Modern UI
- Clean dark-themed interface
- Video browser for easy selection
- Real-time statistics panel
- Configuration options for model selection and video directory

## License

This project is provided as open-source software.