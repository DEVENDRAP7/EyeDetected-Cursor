"""Constants shared across the gaze-controlled cursor app."""
import pyautogui

# Camera
CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Screen
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()

# Smoothing
SMOOTHING_WINDOW = 5

# Blink detection (Eye Aspect Ratio)
EAR_BLINK_THRESHOLD = 0.21
EAR_CONSEC_FRAMES = 2          # frames below threshold to count as a blink
BLINK_CLICK_COOLDOWN = 0.6     # seconds between blink-triggered clicks

# Dwell click (optional)
DWELL_ENABLED = False
DWELL_RADIUS_PX = 40
DWELL_TIME_SEC = 1.5

# Calibration
CALIBRATION_FILE = "calibration.json"
CALIBRATION_GRID_MARGIN = 0.08   # fraction of screen kept clear around edges
CALIBRATION_SAMPLE_SECONDS = 1.0

# Misc
FACE_LOST_WARNING_SECONDS = 2.0
