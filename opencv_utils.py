import cv2 as cv
import numpy as np
import pygetwindow as gw
import pydirectinput
from PIL import ImageGrab


def get_image(window):
    x, y, width, height = window.left, window.top, window.width, window.height

    # Capture a screenshot of the specified window region
    screenshot = ImageGrab.grab(bbox=(x, y, x + width, y + height))

    # Convert the screenshot to a NumPy array
    screenshot = np.array(screenshot)

    # Convert BGR image to RGB
    screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2GRAY)

    return screenshot


def seach_template_in_frame(frame, img_template, match_score=0.7):
    result = cv.matchTemplate(frame, img_template, cv.TM_CCOEFF_NORMED)
    loc = np.where(result >= match_score)
    if len(loc[0]) == 0 or len(loc[1]) == 0:
        return None

    return loc[::-1][0][0], loc[::-1][1][0]

def get_windows(window_title):
    windows = gw.getWindowsWithTitle(window_title)

    if len(windows) < 1:
        print(f"Window {window_title} not found!")
        raise SystemExit

    return windows

def search_and_press_template_in_frame(window, frame, img_template, match_score=0.7):
    pos_x, pos_y = seach_template_in_frame(frame, img_template, match_score)

    h, w = img_template.shape[:2]
    pos_x += w//2
    pos_y += h//2

    pydirectinput.click(window.left + pos_x, window.top + pos_y)
