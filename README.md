# CNC Control Project

A standalone project for controlling a GRBL CNC mill.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the controller:
   ```bash
   python main.py
   ```
   ```

## Webcam Object Detection
Run the YOLOv8 object detection on the webcam:
```bash
cd webcam_yolo
pip install -r requirements.txt
python main.py --source 0
```

## Tests

Run tests with:
```bash
pytest tests/
```
