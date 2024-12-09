import time
import pydirectinput
import pygetwindow
from PIL import ImageGrab
import cv2 as cv
import numpy as np

pydirectinput.FAILSAFE = False


def get_image(window):
    x, y, width, height = window.left, window.top, window.width, window.height
    screenshot = ImageGrab.grab(bbox=(x, y, x + width, y + height))
    screenshot = np.array(screenshot)
    screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2GRAY)
    return screenshot


def search_template_in_window(window, template):
    frame = get_image(window)
    result = cv.matchTemplate(frame, template, cv.TM_CCOEFF_NORMED)

    loc = np.where(result >= 0.9)

    # if no match return None
    if len(loc[0]) == 0 or len(loc[1]) == 0:
        return None

    return loc[::-1][0][0] + window.left, loc[::-1][1][0] + window.top


def press_on_template(window, template, jiggle=False):
    template_x, template_y = search_template_in_window(window, template)

    x_coord = template_x + (template.shape[1] // 2)
    y_coord = template_y + (template.shape[0] // 2)

    # if jiggle move mouse few pixels
    if jiggle:
        for i in range(4):
            pydirectinput.moveTo(x_coord + i, y_coord)
        pydirectinput.leftClick()
        return
    pydirectinput.leftClick(x_coord, y_coord)
    time.sleep(0.05)


if __name__ == '__main__':
    boss_activate_img = cv.imread("resources/boss_can_activate.png", cv.IMREAD_GRAYSCALE)
    call_button_img = cv.imread("resources/call_button.png", cv.IMREAD_GRAYSCALE)
    start_autohunt_img = cv.imread("resources/start_autohunt_button.png", cv.IMREAD_GRAYSCALE)
    stop_autohunt_img = cv.imread("resources/stop_autohunt_button.png", cv.IMREAD_GRAYSCALE)
    yes_button_img = cv.imread("resources/yes_button.png", cv.IMREAD_GRAYSCALE)

    window = pygetwindow.getWindowsWithTitle('Astra2')[0]
    start_biolog_time = time.time()

    while True:

        try:
            # check of any boss availability
            if search_template_in_window(window, boss_activate_img) is not None:
                # 1. stop auto-hunt
                press_on_template(window, stop_autohunt_img)

                # 2. select boss
                press_on_template(window, boss_activate_img)

                # 3. call boss
                press_on_template(window, call_button_img)
                press_on_template(window, yes_button_img)

                # 4. start auto-hunt
                press_on_template(window, start_autohunt_img, jiggle=True)
        except Exception as e:
            print(e)

        time.sleep(5)