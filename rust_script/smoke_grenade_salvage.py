import datetime
import time
from multiprocessing import Process, Queue, Value, Lock

import cv2 as cv
import numpy as np
import pydirectinput
import pygetwindow
from PIL import ImageGrab

template_img = cv.imread('img_1.png', cv.IMREAD_GRAYSCALE)
window = pygetwindow.getWindowsWithTitle("Rust")[0]
x, y = 700, 250
threshold = 0.4


def get_image(window):
    x, y, width, height = window.left, window.top, window.width, window.height

    # Capture a screenshot of the specified window region
    screenshot = ImageGrab.grab(bbox=(x, y, x + width, y + height))

    # Convert the screenshot to a NumPy array
    screenshot = np.array(screenshot)

    # Convert BGR image to RGB
    screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2GRAY)
    # screenshot = cv.resize(screenshot, (0, 0), fx=0.5, fy=0.5)

    return screenshot


def get_template_locs():
    frame = get_image(window)
    crop_img = frame[y:, x:2015]
    result = cv.matchTemplate(crop_img, template_img, cv.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
    if max_val >= threshold:  # Check if any match is found above threshold
        return max_loc
    else:
        return None


loc = get_template_locs()

time.sleep(1)

index = 0
while loc is not None:  # Check if loc is not empty
    x_match, y_match = loc
    # press one grenade
    pydirectinput.rightClick(x + x_match + 30, y + y_match + 30)
    print(f"sold: {index}")
    index += 1
    time.sleep(3.7)

    loc = get_template_locs()

print(f"TOTAL:{index}")
