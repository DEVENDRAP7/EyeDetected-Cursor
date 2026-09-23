# Gaze-Controlled Cursor

Tracks your eye/iris position via webcam (MediaPipe Face Mesh + Iris) and
moves the system cursor accordingly in real time.

## Setup

```bash
pip install -r ../requirements.txt
```

## Usage

```bash
python main.py              # first run triggers calibration automatically
python main.py --recalibrate
python main.py --debug      # show webcam feed with iris/EAR overlay
python main.py --no-blink-click
```

On first run (or with `--recalibrate`), a fullscreen 9-point calibration
screen appears. Look at each red dot and press **Space** to record it;
**Esc** cancels. The fitted mapping is saved to `calibration.json`.

While running:
- Cursor follows your gaze once calibrated.
- Blinking both eyes briefly triggers a click (disable with `--no-blink-click`).
- Press `q` in the debug window, or `Ctrl+C` in the terminal, to quit.

## Files

| File | Purpose |
|---|---|
| `main.py` | App entry point / main loop |
| `tracker.py` | MediaPipe iris + blink (EAR) extraction |
| `calibration.py` | 9-point calibration screen and iris→screen fit |
| `cursor_controller.py` | Applies the calibration mapping and drives the OS cursor |
| `smoother.py` | Moving-average / Kalman smoothing to reduce jitter |
| `config.py` | Tunable constants (smoothing window, thresholds, screen size) |
