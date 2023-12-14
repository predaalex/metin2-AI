import pyautogui
import pydirectinput
import pyautogui
from PIL import ImageGrab
import cv2 as cv
import numpy as np
import pyautogui
from PIL import ImageGrab

# 1. Capture a specific area of the screen
x_start, y_start, width, height = 100, 100, 300, 300  # Define your area coordinates and size
screenshot = ImageGrab.grab(bbox=(x_start, y_start, x_start+width, y_start+height))

# Convert screenshot to format suitable for OpenCV
screen = np.array(screenshot)
screen = cv.cvtColor(screen, cv.COLOR_BGR2RGB)

# 2. Template Matching
template = cv.imread('template_image.jpg')  # Load your template image
template_gray = cv.cvtColor(template, cv.COLOR_BGR2GRAY)
screen_gray = cv.cvtColor(screen, cv.COLOR_BGR2GRAY)

result = cv.matchTemplate(screen_gray, template_gray, cv.TM_CCOEFF_NORMED)
min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)

# Checking if the match is found with sufficient confidence
if max_val > 0.8:  # You can adjust the threshold
    match_x, match_y = max_loc
    match_x += x_start  # Adjusting to the full screen coordinates
    match_y += y_start

    # 3. Simulate a Mouse Click
    pyautogui.click(match_x, match_y)

# Note: This is a very basic example and might need adjustments based on your requirements.
