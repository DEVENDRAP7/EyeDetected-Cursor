"""Maps smoothed iris coordinates to screen coordinates and drives the cursor."""
import json
import os

import numpy as np
import pyautogui

from config import CALIBRATION_FILE, SCREEN_HEIGHT, SCREEN_WIDTH

pyautogui.FAILSAFE = False


def _poly_features(x, y):
    return np.array([1.0, x, y, x * x, y * y, x * y])


class CalibrationNotFoundError(RuntimeError):
    pass


class CursorController:
    def __init__(self, calibration_file=CALIBRATION_FILE):
        if not os.path.exists(calibration_file):
            raise CalibrationNotFoundError(
                f"No calibration data found at '{calibration_file}'. Run calibration first."
            )
        with open(calibration_file) as f:
            data = json.load(f)
        self._coeffs_x = np.array(data["coeffs_x"])
        self._coeffs_y = np.array(data["coeffs_y"])

    def map_to_screen(self, iris_xy):
        features = _poly_features(*iris_xy)
        sx = float(features @ self._coeffs_x)
        sy = float(features @ self._coeffs_y)
        sx = min(max(sx, 0), SCREEN_WIDTH - 1)
        sy = min(max(sy, 0), SCREEN_HEIGHT - 1)
        return (sx, sy)

    def move(self, screen_xy):
        pyautogui.moveTo(screen_xy[0], screen_xy[1], duration=0)

    def click(self):
        pyautogui.click()
