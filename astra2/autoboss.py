import builtins
import time
from datetime import datetime
import pydirectinput
import pygetwindow
from PIL import ImageGrab
import cv2 as cv
import numpy as np
import pyautogui
import inspect

pydirectinput.FAILSAFE = False


def print(*args, **kwargs):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    builtins.print(f"[{timestamp}] ", *args, **kwargs)


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


def press_on_template(window, template, jiggle=False, click_type="Left"):
    template_x, template_y = search_template_in_window(window, template)

    x_coord = template_x + (template.shape[1] // 2)
    y_coord = template_y + (template.shape[0] // 2)

    # if jiggle move mouse few pixels
    if jiggle:
        for i in range(4):
            pydirectinput.moveTo(x_coord + i, y_coord)
        if click_type == "Left":
            pydirectinput.leftClick()
        elif click_type == "Right":
            pydirectinput.rightClick()
        return
    if click_type == "Left":
        pydirectinput.leftClick(x_coord, y_coord)
    elif click_type == "Right":
        pydirectinput.rightClick(x_coord, y_coord)
    time.sleep(0.05)


def safe_press_on_template(window, img, jiggle=False, click_type="Left"):
    # Attempt to identify the variable name dynamically
    callers_local_vars = inspect.currentframe().f_back.f_locals.items()
    name = next((var_name for var_name, var_val in callers_local_vars if var_val is img), None)

    try:
        # Attempt to press on the template
        press_on_template(window, img, jiggle, click_type)
    except Exception as e:
        # Log the exception with the name of the image if available, otherwise use a default name
        name_to_print = name if name else "unknown_template"
        print(f"Failed to press on template {name_to_print}: {e}")


class PagesIterator:
    def __init__(self, start=1, end=5):
        self.start = start
        self.end = end
        self.current = start
        self.forward = True  # Direction: True for forward, False for backward

    def __iter__(self):
        return self

    def __next__(self):
        if self.forward:
            if self.current < self.end:
                self.current += 1
            else:
                self.forward = False
                self.current -= 1
        else:
            if self.current > self.start:
                self.current -= 1
            else:
                self.forward = True
                self.current += 1
        return self.current


if __name__ == '__main__':
    boss_activate_img = cv.imread("resources/boss_can_activate.png", cv.IMREAD_GRAYSCALE)
    call_button_img = cv.imread("resources/call_button.png", cv.IMREAD_GRAYSCALE)
    start_autohunt_img = cv.imread("resources/start_autohunt_button.png", cv.IMREAD_GRAYSCALE)
    stop_autohunt_img = cv.imread("resources/stop_autohunt_button.png", cv.IMREAD_GRAYSCALE)
    open_autohunt_img = cv.imread("resources/open_autohunt_button.png", cv.IMREAD_GRAYSCALE)
    yes_button_img = cv.imread("resources/yes_button.png", cv.IMREAD_GRAYSCALE)

    window = pygetwindow.getWindowsWithTitle('Astra2')[0]
    window.activate()
    iterator = PagesIterator(start=0, end=2)
    start_biolog_time = time.time()

    try:
        while True:

            # check if the dungeon window is open
            if search_template_in_window(window, call_button_img) is None:
                pydirectinput.press("f7")
                print(f"dungeon window was opened")
                time.sleep(0.2)
                continue

            # check if the auto-hunt window is open
            elif (search_template_in_window(window, start_autohunt_img) is None and
                  search_template_in_window(window, stop_autohunt_img) is None):
                safe_press_on_template(window, open_autohunt_img)
                print(f"auto-hunt window was opened")
                time.sleep(0.2)
                continue
            # check of any boss availability
            elif search_template_in_window(window, boss_activate_img) is not None:
                # 1. stop auto-hunt
                safe_press_on_template(window, stop_autohunt_img)

                # 2.1 open dungeon information window
                safe_press_on_template(window, call_button_img, click_type="Right")

                # 2.2 select boss
                # no need to handle exception because it wouldn't enter main if
                safe_press_on_template(window, boss_activate_img)

                # 3. call boss
                safe_press_on_template(window, call_button_img)
                safe_press_on_template(window, yes_button_img)

                # 4. start auto-hunt
                safe_press_on_template(window, start_autohunt_img, jiggle=True)

                # 5. reset format with dungeon info open
                safe_press_on_template(window, call_button_img, click_type="Right")


            # scroll to see other pages
            else:
                next(iterator)

                # find dungeon window position
                x_dungeon, y_dungeon = search_template_in_window(window, call_button_img)
                pydirectinput.moveTo(x_dungeon, y_dungeon)
                pydirectinput.rightClick()
                if iterator.forward:
                    pyautogui.scroll(-1)
                else:
                    pyautogui.scroll(1)
            time.sleep(5)

    except KeyboardInterrupt:
        print("\nKeyboard interrupt detected. Exiting...")
        exit(0)
    except Exception as e:
        print(e)
        print("\nUnknown problem.\nExiting...")
        safe_press_on_template(window, start_autohunt_img, jiggle=True)
