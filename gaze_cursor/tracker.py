"""MediaPipe Face Mesh + Iris based gaze tracking."""
import mediapipe as mp
import numpy as np

# Iris ring landmarks (refine_landmarks=True adds these)
LEFT_IRIS = [474, 475, 476, 477]
RIGHT_IRIS = [469, 470, 471, 472]

# Eye corner + lid landmarks used for Eye Aspect Ratio (EAR)
LEFT_EYE_EAR = [362, 385, 387, 263, 373, 380]
RIGHT_EYE_EAR = [33, 160, 158, 133, 153, 144]


def _eye_aspect_ratio(landmarks, indices):
    p1, p2, p3, p4, p5, p6 = (np.array([landmarks[i].x, landmarks[i].y]) for i in indices)
    vertical = np.linalg.norm(p2 - p6) + np.linalg.norm(p3 - p5)
    horizontal = np.linalg.norm(p1 - p4)
    if horizontal == 0:
        return 0.0
    return vertical / (2.0 * horizontal)


class GazeTracker:
    """Wraps MediaPipe FaceMesh to expose iris center + blink state per frame."""

    def __init__(self):
        self._face_mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

    def process(self, frame_bgr):
        """Returns a dict with iris_xy (normalized, 0-1), ear, and face_found,
        or {"face_found": False} if no face was detected."""
        rgb = frame_bgr[:, :, ::-1]
        results = self._face_mesh.process(rgb)

        if not results.multi_face_landmarks:
            return {"face_found": False}

        landmarks = results.multi_face_landmarks[0].landmark

        left_center = self._iris_center(landmarks, LEFT_IRIS)
        right_center = self._iris_center(landmarks, RIGHT_IRIS)
        iris_xy = ((left_center[0] + right_center[0]) / 2.0,
                   (left_center[1] + right_center[1]) / 2.0)

        left_ear = _eye_aspect_ratio(landmarks, LEFT_EYE_EAR)
        right_ear = _eye_aspect_ratio(landmarks, RIGHT_EYE_EAR)
        ear = (left_ear + right_ear) / 2.0

        return {
            "face_found": True,
            "iris_xy": iris_xy,
            "left_iris_xy": left_center,
            "right_iris_xy": right_center,
            "ear": ear,
            "landmarks": landmarks,
        }

    @staticmethod
    def _iris_center(landmarks, indices):
        xs = [landmarks[i].x for i in indices]
        ys = [landmarks[i].y for i in indices]
        return (sum(xs) / len(xs), sum(ys) / len(ys))

    def close(self):
        self._face_mesh.close()
