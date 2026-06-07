# YOLO Model Guide

This repository keeps YOLO inference optional.

## Default Mode

The default launch mode uses no model and publishes empty detections while still forwarding the annotated image topic.

```bash
ros2 launch service_robot_perception yolo_detection.launch.py
```

## Lightweight Models

Use a small official Ultralytics model for quick testing, then replace it with your own trained weight if needed.

Typical commands:

```bash
pip3 install ultralytics
yolo detect predict model=yolov8n.pt source=0
```

Official model downloads and examples:

- https://docs.ultralytics.com/models/yolov8/
- https://docs.ultralytics.com/models/yolo11/

## Repository Policy

- Do not commit `.pt`, `.onnx`, `.engine`, `.pth`, or similar weight files.
- Store the model path in launch arguments or a local config file outside version control.
- If you need a custom model, document the class list, export format, and validation source in `docs/verification_report.md`.
