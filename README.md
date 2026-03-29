# AI CCTV Traffic Enforcement Starter

This project is a starter implementation for an AI-based traffic monitoring system that can:

- read a live CCTV stream or video file
- detect motorcycles and riders
- estimate vehicle speed inside a calibrated road segment
- detect helmet / no-helmet violations
- read number plates using OCR
- save violation reports that can later be sent to an RTO office system

## Important note

This is a starter project, not a production-ready law-enforcement system. Real deployment requires:

- camera calibration for each road
- a trained helmet / no-helmet model
- a trained number plate detector
- legal approval, audit logs, and human review before sending fines

## Suggested architecture

1. CCTV stream -> OpenCV video capture
2. Object detection -> YOLO model for bikes, riders, helmet, number plate
3. Tracking -> assign a stable ID to each vehicle
4. Speed estimation -> calculate time taken to cross a known distance
5. OCR -> read the vehicle number plate
6. Reporting -> save JSON evidence and optionally POST to an API

## Project structure

```text
src/
  main.py
  pipeline.py
  detectors.py
  speed_estimator.py
  ocr_engine.py
  reporting.py
  models.py
  utils.py
data/
  violations/
config.example.yaml
requirements.txt
```

## Install

Create a virtual environment and install dependencies:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Configure

Copy the sample config and edit it for your camera:

```powershell
Copy-Item config.example.yaml config.yaml
```

Update:

- `source`: RTSP URL, webcam index, or video file path
- `distance_meters`: real road distance between the two virtual lines
- `line_y_start` and `line_y_end`: vertical positions used for speed estimation
- model paths for your custom YOLO weights
- `speed_limit_kmph`

## Run

```powershell
python -m src.main --config config.yaml
```

Press `q` to stop the video window.

## How speed is estimated

The starter logic measures how long a tracked vehicle takes to move between two configured virtual lines:

```text
speed_kmph = (distance_meters / time_seconds) * 3.6
```

For best accuracy:

- mount the camera high and stable
- keep the target lane clearly visible
- use one lane or calibrate lane-wise
- use top-down or near-top-down angles when possible

## RTO integration

Right now the project saves violations to `data/violations/violations.jsonl` and frame snapshots to `data/violations/images/`.

Later, you can connect `reporting.py` to:

- an RTO web API
- email workflow
- dashboard review system
- SMS / challan generation system

## Recommended next improvements

- train a custom `helmet` / `no_helmet` detector
- add plate detector for Indian number plates
- replace the simple tracker with ByteTrack or DeepSORT
- add FastAPI backend and review dashboard
- store reports in PostgreSQL
- add human approval before final submission
