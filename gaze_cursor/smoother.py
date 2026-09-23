"""Jitter reduction for the raw iris coordinate stream."""
from collections import deque

from config import SMOOTHING_WINDOW


class MovingAverageSmoother:
    """Simple moving average over the last N (x, y) points."""

    def __init__(self, window=SMOOTHING_WINDOW):
        self._window = deque(maxlen=window)

    def update(self, point):
        self._window.append(point)
        xs, ys = zip(*self._window)
        return (sum(xs) / len(xs), sum(ys) / len(ys))

    def reset(self):
        self._window.clear()


class KalmanSmoother2D:
    """Lightweight constant-velocity Kalman filter for smoother tracking."""

    def __init__(self, process_noise=1e-3, measurement_noise=1e-2):
        # State: [x, y, vx, vy]
        self._x = None
        self._p = None
        self._q = process_noise
        self._r = measurement_noise

    def update(self, point):
        import numpy as np

        z = np.array(point, dtype=float)

        if self._x is None:
            self._x = np.array([z[0], z[1], 0.0, 0.0])
            self._p = np.eye(4)
            return point

        f = np.array([[1, 0, 1, 0],
                      [0, 1, 0, 1],
                      [0, 0, 1, 0],
                      [0, 0, 0, 1]])
        h = np.array([[1, 0, 0, 0],
                      [0, 1, 0, 0]])

        x_pred = f @ self._x
        p_pred = f @ self._p @ f.T + self._q * np.eye(4)

        y = z - h @ x_pred
        s = h @ p_pred @ h.T + self._r * np.eye(2)
        k = p_pred @ h.T @ np.linalg.inv(s)

        self._x = x_pred + k @ y
        self._p = (np.eye(4) - k @ h) @ p_pred

        return (float(self._x[0]), float(self._x[1]))

    def reset(self):
        self._x = None
        self._p = None
