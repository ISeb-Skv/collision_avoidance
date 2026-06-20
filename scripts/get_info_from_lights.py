import cv2
from ultralytics import YOLO
import numpy as np
import pandas as pd
from pathlib import Path
import time
from collections import deque
import warnings
import re
from google.colab import drive
drive.mount('/content/drive')
PROJECT_PATH = '/content/drive/MyDrive/collision_avoidance_project'
DANGER_ZONE = (450, 800, 1550, 1080)        # (x1, y1, x2, y2)
COLLISION_WIDTH_THRESHOLD_PX = 175
MODEL_PATH = "models/best.pt"
VIDEOS_DIR = Path("videos")
RESULTS_DIR = Path("results")
HISTORY_LEN = 10
PREDICTION_HORIZON = 5
ARROW_REVERSE = False
import os
os.chdir(PROJECT_PATH)
print(f"Текущая директория: {os.getcwd()}")

RESULTS_DIR.mkdir(exist_ok=True, parents=True)
(RESULTS_DIR / "logs").mkdir(exist_ok=True)
(RESULTS_DIR / "annotated_videos").mkdir(exist_ok=True)

model = YOLO(MODEL_PATH)

def get_robot_info_from_lights(boxes):
    """Возвращает (center, width, orientation) если найдены все три диода."""
    green = red = blue = None
    for box in boxes:
        class_name = model.names[int(box.cls[0])]
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        cx, cy = (x1 + x2)//2, (y1 + y2)//2
        if class_name == 'green_light':
            green = (cx, cy)
        elif class_name == 'red_light':
            red = (cx, cy)
        elif class_name == 'blue_light':
            blue = (cx, cy)
    if green and red and blue:
        center = ((green[0] + red[0] + blue[0]) // 3,
                  (green[1] + red[1] + blue[1]) // 3)
        width = np.hypot(red[0] - blue[0], red[1] - blue[1])
        orientation = (green[0] - center[0], green[1] - center[1])
        return center, width, orientation
    return None, None, None
