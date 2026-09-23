# EyeDetected-Cursor

Gaze-controlled cursor, in two forms:

- **[`gaze_cursor/`](gaze_cursor/)** — a Python desktop app. Tracks your eye/iris
  via a webcam (MediaPipe + OpenCV) and moves your computer's real system
  cursor (`pyautogui`). Requires Python and a webcam-equipped desktop/laptop;
  see [`gaze_cursor/README.md`](gaze_cursor/README.md) for setup.

- **[`docs/`](docs/)** — a phone/browser demo. Pure client-side HTML/JS
  (MediaPipe Tasks Vision via WASM, no install, no server). Uses your
  phone's front camera to move a cursor **within the webpage**, not your
  phone's OS cursor — browsers don't allow a page to control that. See
  [`docs/README.md`](docs/README.md) to try it or host it yourself via
  GitHub Pages.
