"""9-point calibration screen: maps iris coordinates to screen coordinates."""
import json
import time
import tkinter as tk

import numpy as np

from config import (
    CALIBRATION_FILE,
    CALIBRATION_GRID_MARGIN,
    CALIBRATION_SAMPLE_SECONDS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)


def _poly_features(x, y):
    """Quadratic feature expansion used for the iris -> screen fit."""
    return np.array([1.0, x, y, x * x, y * y, x * y])


def _grid_points():
    m = CALIBRATION_GRID_MARGIN
    xs = [m, 0.5, 1 - m]
    ys = [m, 0.5, 1 - m]
    return [(SCREEN_WIDTH * x, SCREEN_HEIGHT * y) for y in ys for x in xs]


class CalibrationSession:
    """Runs a fullscreen 9-dot calibration and fits an iris -> screen mapping.

    `get_iris_sample` must be a zero-arg callable returning the current
    normalized iris (x, y) tuple, or None if no face is detected.
    """

    def __init__(self, get_iris_sample):
        self._get_iris_sample = get_iris_sample
        self._samples = []  # list of (iris_xy, screen_xy)

    def run(self):
        root = tk.Tk()
        root.attributes("-fullscreen", True)
        root.configure(bg="black")
        canvas = tk.Canvas(root, bg="black", highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        instructions = canvas.create_text(
            SCREEN_WIDTH // 2, 40,
            text="Look at each dot and press SPACE to record it (Esc to cancel)",
            fill="white", font=("Helvetica", 18),
        )

        points = _grid_points()
        state = {"index": 0, "cancelled": False}
        dot_radius = 14
        dot_id = None

        def draw_dot(px, py):
            nonlocal dot_id
            if dot_id is not None:
                canvas.delete(dot_id)
            dot_id = canvas.create_oval(
                px - dot_radius, py - dot_radius, px + dot_radius, py + dot_radius,
                fill="red", outline="white", width=2,
            )

        def record_current_point(_event=None):
            if state["index"] >= len(points):
                return
            samples = []
            deadline = time.time() + CALIBRATION_SAMPLE_SECONDS
            while time.time() < deadline:
                sample = self._get_iris_sample()
                if sample is not None:
                    samples.append(sample)
                root.update()
            if samples:
                xs, ys = zip(*samples)
                avg_iris = (sum(xs) / len(xs), sum(ys) / len(ys))
                self._samples.append((avg_iris, points[state["index"]]))
            state["index"] += 1
            if state["index"] >= len(points):
                root.quit()
            else:
                draw_dot(*points[state["index"]])

        def cancel(_event=None):
            state["cancelled"] = True
            root.quit()

        root.bind("<space>", record_current_point)
        root.bind("<Escape>", cancel)

        draw_dot(*points[0])
        root.mainloop()
        root.destroy()

        if state["cancelled"] or len(self._samples) < 6:
            return False

        self._fit_and_save()
        return True

    def _fit_and_save(self):
        a_matrix = np.array([_poly_features(*iris) for iris, _screen in self._samples])
        sx = np.array([screen[0] for _iris, screen in self._samples])
        sy = np.array([screen[1] for _iris, screen in self._samples])

        coeffs_x, *_ = np.linalg.lstsq(a_matrix, sx, rcond=None)
        coeffs_y, *_ = np.linalg.lstsq(a_matrix, sy, rcond=None)

        data = {
            "screen_size": [SCREEN_WIDTH, SCREEN_HEIGHT],
            "coeffs_x": coeffs_x.tolist(),
            "coeffs_y": coeffs_y.tolist(),
            "samples": [
                {"iris": list(iris), "screen": list(screen)}
                for iris, screen in self._samples
            ],
        }
        with open(CALIBRATION_FILE, "w") as f:
            json.dump(data, f, indent=2)
