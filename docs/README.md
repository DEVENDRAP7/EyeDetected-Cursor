# Gaze Cursor — Web Demo

A single self-contained page (`index.html`) that tracks your gaze using
your phone or laptop's front camera and moves a cursor **within this page**.
Everything runs client-side in the browser via MediaPipe's Tasks Vision
WASM build — no backend, no install, nothing leaves the device.

It cannot move your phone's real system cursor. No webpage can — browsers
don't grant that level of OS control. This demo instead moves an on-page
cursor and lets you "click" on-page demo targets by dwelling on them or
blinking, so you can feel the tracking working.

## Try it on your phone

The camera API only works over **HTTPS** (or `localhost`), so you need to
serve this file, not just open it from disk. The easiest way is GitHub Pages:

1. In the repo: **Settings → Pages**
2. **Source**: Deploy from a branch
3. **Branch**: `main`, folder **`/docs`** → Save
4. After a minute, GitHub gives you a URL like
   `https://<your-username>.github.io/<repo-name>/`
5. Open that URL on your phone, tap **"Enable camera & start"**, allow
   camera access, then **Calibrate**.

## Or run it locally

```bash
cd docs
python3 -m http.server 8000
```

Open `http://localhost:8000` on the same computer (camera access is allowed
on `localhost` without HTTPS). To reach it from your *phone* on the same
Wi-Fi, `http://<your-computer's-LAN-IP>:8000` will **not** get camera access
(not a secure context) — use GitHub Pages, or a tunnel like `ngrok http 8000`,
for that.

## How it works

- `FaceLandmarker` (MediaPipe Tasks Vision) tracks 478 face landmarks per
  frame, including iris points — same landmark indices the desktop app's
  `tracker.py` uses.
- **Calibration**: a 9-point grid, same idea as the desktop app's
  `calibration.py` — look at each dot and tap it; a quadratic least-squares
  fit maps iris position to page coordinates. Saved to `localStorage` so you
  don't have to redo it every visit.
- **Smoothing**: a small moving average, like `smoother.py`.
- **Interaction**: dwell on a demo target for ~1.3s, or blink, to "click" it.

## Notes

- Works best in good, even lighting, with your face centered in frame.
- If tracking direction feels mirrored (cursor moves opposite to your gaze),
  flip the sign in the `ix = 1 - ix;` line in `index.html` — front-camera
  mirroring can vary slightly by device/browser.
- GPU delegate is tried first for performance, with an automatic fallback to
  CPU on devices/browsers that don't support it.
