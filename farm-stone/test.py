import time

import cv2 as cv
import numpy as np
import pygetwindow as gw
from PIL import ImageGrab, Image
import pyautogui
import pydirectinput

threshold = 0.8
x_click_offset, y_click_offset = 40, 40
helper_points = False

# Set the window title you want to capture
window_title = "Zenaris"

# Find the window by its title
window = gw.getWindowsWithTitle(window_title)
template = cv.imread("resources/template.png", cv.IMREAD_GRAYSCALE)
template_stone_check = cv.imread("resources/template_stone_check.png", cv.IMREAD_GRAYSCALE)


# template = cv.resize(template, (0, 0), fx=0.5, fy=0.5)
# cv.imshow("template", template)


def get_center(frame):
    height, weight = frame.shape
    x_center_calculat = weight // 2
    y_center_calculat = height // 2

    return x_center_calculat, y_center_calculat


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


def get_stone_position_by_distance(frame, x_center, y_center):
    global x_click_offset
    frame = frame[100:, :]
    y_center -= 100
    result = cv.matchTemplate(frame, template, cv.TM_CCOEFF_NORMED)

    loc = np.where(result >= threshold)

    distances = {}

    for x_match, y_match in zip(*loc[::-1]):
        if x_match < x_center:  # left side
            color = (0, 0, 0)
            x_click_offset = 55
        else:
            color = (255, 255, 255)  # right side
            x_click_offset = 40

        x_match += x_click_offset
        y_match += y_click_offset

        distance = int(np.sqrt((x_center - x_match) ** 2 + (y_center - y_match) ** 2))
        distances[distance] = (x_match, y_match + 100)

        try:
            if helper_points:
                cv.circle(img=frame, center=(x_match, y_match),
                          radius=10, color=color, thickness=2)

                cv.circle(img=frame, center=(x_center, y_center),
                          radius=10, color=color, thickness=2)
        except:
            print(f"Open {window_title} window")

    distances = dict(sorted(distances.items()))

    return distances


def select_metin(x, y):

    pydirectinput.moveTo(window.left + x, window.top + y)
    pydirectinput.rightClick()


def check_selected_metin(frame):
    stone_hp_area = frame[:100, x_center - 190: x_center + 190]

    try:
        result = cv.matchTemplate(stone_hp_area, template_stone_check, cv.TM_CCOEFF_NORMED)
        return np.any(result > 0.9)
    except:
        print("deschide window metin")
        return False


def print_circles(closest_x, closest_y):
    color = (0, 0, 0)
    # if closest_x < x_center:  # left side
    #     x_click_offset = 50
    # else:
    #     color = (255, 255, 255)  # right side
    #     x_click_offset = 40
    # closest_x += x_click_offset
    # closest_y += y_click_offset
    try:
        if helper_points:
            cv.circle(img=frame, center=(closest_x, closest_y),
                      radius=20, color=color, thickness=2)

            cv.circle(img=frame, center=(x_center, y_center),
                      radius=20, color=color, thickness=2)
    except:
        print(f"Open {window_title} window")


if len(window) == 0:
    print(f"Window '{window_title}' not found.")
else:
    window = window[0]  # Assuming there's only one window with the given title

    while True:

        # Get the window's position and size
        frame = get_image(window)
        time.sleep(0.1)
        # Get the center of window
        x_center, y_center = get_center(frame)

        # Get the closest stone
        distances_sorted = get_stone_position_by_distance(frame, x_center, y_center)
        iterator = iter(distances_sorted)
        closest_dist = next(iterator, None)

        if closest_dist is not None:
            closest_x, closest_y = distances_sorted[closest_dist]

            # Right click on stone
            select_metin(closest_x, closest_y)
            time.sleep(0.1)

            # check if the right metin was clicked
            try:
                while not check_selected_metin(get_image(window)):
                    time.sleep(0.3)
                    closest_dist = next(iterator, None)
                    closest_x, closest_y = distances_sorted[closest_dist]
                    frame = get_image(window)
                    select_metin(closest_x, closest_y)
                    time.sleep(0.1)
                    print("nu i ok")
            except:
                print("sa o fut pe ma-ta")
                continue

            # left-click the validated stone
            pydirectinput.leftClick()

            i = 0
            while check_selected_metin(get_image(window)):
                print("dudu suge putulica", i)
                i += 1
                time.sleep(1)

            pydirectinput.press('z')

            print("dudu o supt o pe toata")
        else:
            print("No stones in range")

        # Display the captured frame
        if helper_points:
            cv.imshow("Window Capture", frame)

        # Exit the loop when 'q' key is pressed
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

# Close all OpenCV windows
cv.destroyAllWindows()
