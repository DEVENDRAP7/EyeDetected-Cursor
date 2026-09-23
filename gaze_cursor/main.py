"""Entry point: gaze-controlled cursor app."""
import argparse
import os
import time

import cv2

from calibration import CalibrationSession
from config import (
    BLINK_CLICK_COOLDOWN,
    CALIBRATION_FILE,
    CAMERA_INDEX,
    EAR_BLINK_THRESHOLD,
    EAR_CONSEC_FRAMES,
    FACE_LOST_WARNING_SECONDS,
    FRAME_HEIGHT,
    FRAME_WIDTH,
)
from cursor_controller import CursorController
from smoother import MovingAverageSmoother
from tracker import GazeTracker


def draw_debug_overlay(frame, result):
    if not result.get("face_found"):
        cv2.putText(frame, "No face detected", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        return frame

    h, w = frame.shape[:2]
    for label, (x, y) in (("L", result["left_iris_xy"]), ("R", result["right_iris_xy"])):
        cv2.circle(frame, (int(x * w), int(y * h)), 3, (0, 255, 0), -1)
    cv2.putText(frame, f"EAR: {result['ear']:.2f}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    return frame


def run_calibration(cap, tracker):
    def get_iris_sample():
        ok, frame = cap.read()
        if not ok:
            return None
        frame = cv2.flip(frame, 1)
        result = tracker.process(frame)
        return result["iris_xy"] if result.get("face_found") else None

    print("Starting calibration. Look at each dot and press SPACE.")
    session = CalibrationSession(get_iris_sample)
    success = session.run()
    if success:
        print(f"Calibration saved to {CALIBRATION_FILE}")
    else:
        print("Calibration cancelled or not enough samples collected.")
    return success


def main():
    parser = argparse.ArgumentParser(description="Gaze-controlled cursor")
    parser.add_argument("--debug", action="store_true", help="Show webcam debug overlay window")
    parser.add_argument("--recalibrate", action="store_true", help="Force re-running calibration")
    parser.add_argument("--no-blink-click", action="store_true", help="Disable blink-to-click")
    args = parser.parse_args()

    cap = cv2.VideoCapture(CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    if not cap.isOpened():
        raise RuntimeError("Could not open webcam.")

    tracker = GazeTracker()

    try:
        if args.recalibrate or not os.path.exists(CALIBRATION_FILE):
            if not run_calibration(cap, tracker):
                return
        controller = CursorController()
        smoother = MovingAverageSmoother()

        blink_frame_count = 0
        last_click_time = 0.0
        last_face_seen = time.time()

        print("Gaze cursor running. Press 'q' in the debug window (or Ctrl+C) to quit.")

        while True:
            ok, frame = cap.read()
            if not ok:
                continue
            frame = cv2.flip(frame, 1)

            result = tracker.process(frame)

            if not result.get("face_found"):
                if time.time() - last_face_seen > FACE_LOST_WARNING_SECONDS:
                    print("Warning: face not detected. Check lighting/camera position.")
                if args.debug:
                    cv2.imshow("Gaze Cursor Debug", draw_debug_overlay(frame, result))
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break
                continue

            last_face_seen = time.time()

            smooth_xy = smoother.update(result["iris_xy"])
            screen_xy = controller.map_to_screen(smooth_xy)
            controller.move(screen_xy)

            if not args.no_blink_click:
                if result["ear"] < EAR_BLINK_THRESHOLD:
                    blink_frame_count += 1
                else:
                    if (blink_frame_count >= EAR_CONSEC_FRAMES
                            and time.time() - last_click_time > BLINK_CLICK_COOLDOWN):
                        controller.click()
                        last_click_time = time.time()
                    blink_frame_count = 0

            if args.debug:
                cv2.imshow("Gaze Cursor Debug", draw_debug_overlay(frame, result))
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

    except KeyboardInterrupt:
        pass
    finally:
        tracker.close()
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
