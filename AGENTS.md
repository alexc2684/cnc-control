# CNC Project Documentation for Agents

This repository contains code to control a CNC router (mill) using a Python-based driver that communicates over serial (GRBL).

## Key Components

### Source Code (`src/cnc_control`)
- **`driver.py`**: Contains the `Mill` class, which is the main interface for controlling the CNC machine.
    - **Usage**: Use `with Mill() as mill:` to connect.
    - **Methods**: `mill.move_to_position(x, y, z)`, `mill.home()`, `mill.current_coordinates()`.
- **`tools.py`**: Defines `Coordinates`, `ToolManager`, and `Instruments`. Handles tool offsets.
- **`mock.py`**: Contains `MockMill` for offline testing.

### Testing
- **`test_cnc_move.py`**: A sample script to move the CNC mill 1mm in the X direction.
    - **Run with**: `python3 test_cnc_move.py` (requires CNC connection)
- **`tests/verify_cnc_move.py`**: Verifies logic of the move script using mocks.

## Usage Guide for Agents

1.  **Connecting**: Always use the context manager `with Mill() as mill:` to ensure proper connection and cleanup.
2.  **Moving**: Use `mill.move_to_position(x, y, z)` for safe moves. The driver handles validation against the working volume (negative coordinates mostly).
    - **Coordinates**: The machine typically operates in negative space relative to Home (0,0,0). e.g., X goes from 0 to -415.
3.  **Offsets**: Tools have offsets managed by `ToolManager`.

### Webcam YOLO Module
- **`webcam_yolo/`**: Contains the object detection project using YOLOv8.
    - **`main.py`**: Runs the live webcam feed with object detection.
    - **Usage**: `python webcam_yolo/main.py --source <camera_index>` (0 is usually the Brio 101).

## Environment
- **Python**: 3.x
- **Dependencies**: `pyserial`, `ultralytics`, `opencv-python`.
