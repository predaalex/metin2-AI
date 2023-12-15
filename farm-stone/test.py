import time
import cv2 as cv
import numpy as np
import pygetwindow as gw
import pydirectinput
from PIL import ImageGrab

helper_points = False
chat_sell = True
threshold = 0.8
x_click_offset, y_click_offset = 40, 40
skill_timer = 20 * 60
clear_mobs_timer = 600
reset_after = 45

# Set the window title you want to capture
window_title = "Zenaris"

# Find the window by its title
windows = gw.getWindowsWithTitle(window_title)
template = cv.imread("resources/template2.png", cv.IMREAD_GRAYSCALE)
template_stone_check = cv.imread("resources/template_stone_check2.png", cv.IMREAD_GRAYSCALE)


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


def get_stone_position_by_distance(window, frame, x_center, y_center):
    global x_click_offset, y_click_offset
    frame = frame[100:, :-100]
    y_center -= 100
    result = cv.matchTemplate(frame, template, cv.TM_CCOEFF_NORMED)

    loc = np.where(result >= threshold)

    distances = {}

    for x_match, y_match in zip(*loc[::-1]):
        if x_match < window.width / 3:  # 1/3 of screen ( left )
            color = (0, 0, 0)
            x_click_offset = 60
        elif x_match < window.width * 2 / 3:  # 2/3 of screen ( middle )
            color = (125, 125, 125)
            x_click_offset = 50
        else:
            color = (255, 255, 255)  # 3/3 of screen ( right )
            x_click_offset = 40

        if y_match < window.height / 3:  # (top)
            y_click_offset = 40
        elif y_match < window.height * 2 / 3:  # (middle)
            y_click_offset = 65
        else:
            y_click_offset = 90  # (bottom)

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


def select_metin(window, x, y):
    pydirectinput.moveTo(window.left + x, window.top + y)
    pydirectinput.rightClick()


def check_selected_metin(frame, x_center):
    stone_hp_area = frame[:100, x_center - 190: x_center + 190]

    try:
        result = cv.matchTemplate(stone_hp_area, template_stone_check, cv.TM_CCOEFF_NORMED)
        return np.any(result > 0.9)
    except:
        print("Open game window")
        return False


def print_circles(frame, closest_x, closest_y, x_center, y_center):
    color = (0, 0, 0)

    try:
        if helper_points:
            cv.circle(img=frame, center=(closest_x, closest_y),
                      radius=20, color=color, thickness=2)

            cv.circle(img=frame, center=(x_center, y_center),
                      radius=20, color=color, thickness=2)
    except:
        print(f"Open {window_title} window")


def game_automation(window):
    start_spell_timer = time.time()
    start_mob_clean_timer = time.time()
    while True:

        # Get the window's position and size
        frame = get_image(window)
        # Get the center of window
        x_center, y_center = get_center(frame)

        # Get the closest stone
        distances_sorted = get_stone_position_by_distance(window, frame, x_center, y_center)
        iterator = iter(distances_sorted)
        closest_dist = next(iterator, None)

        if closest_dist is not None:
            closest_x, closest_y = distances_sorted[closest_dist]

            # Right click on stone
            select_metin(window, closest_x, closest_y)
            time.sleep(0.1)

            # check if the right metin was clicked
            try:
                while not check_selected_metin(get_image(window), x_center):
                    time.sleep(0.3)
                    closest_dist = next(iterator, None)
                    closest_x, closest_y = distances_sorted[closest_dist]
                    frame = get_image(window)
                    select_metin(window, closest_x, closest_y)
                    time.sleep(0.1)
                    print("Did NOT selected the metin")
            except:
                print("Could NOT select any metin stones")
                pydirectinput.press('q')
                continue

            # left-click the validated stone
            pydirectinput.leftClick()

            # the stone was not destroyed under 30 seconds,
            # so it changes camera position and begins the loop again
            break_loop = False
            i = 0
            while check_selected_metin(get_image(window), x_center):
                print(f"Stone hit for {i}s")
                i += 1
                time.sleep(1)
                if i > reset_after:
                    pydirectinput.press('z')
                    pydirectinput.press('esc')
                    pydirectinput.press('q', presses=10)
                    break_loop = True
            if break_loop:
                continue

            print("Stone destroyed")
            print("timer mobi", time.time() - start_mob_clean_timer)
            print("timer spell", time.time() - start_spell_timer)
            pydirectinput.press('z')

            # After stone was destroyed, write last message in chat
            if chat_sell:
                time.sleep(0.1)
                pydirectinput.press('enter')
                time.sleep(0.1)
                pydirectinput.press('up')
                time.sleep(0.1)
                pydirectinput.press('enter')
                time.sleep(0.1)
                pydirectinput.press('enter')
                time.sleep(0.1)

            if time.time() - start_spell_timer > skill_timer:  # After expiration time, spells are casted again
                print("casting spells")
                # unmount horse
                pydirectinput.keyDown("ctrl")
                pydirectinput.press('g')
                time.sleep(0.1)
                pydirectinput.keyUp("ctrl")
                time.sleep(0.1)

                # cast spells
                pydirectinput.press('3')
                time.sleep(2.5)
                pydirectinput.press('4')
                time.sleep(2.5)

                # mount horse
                pydirectinput.keyDown("ctrl")
                pydirectinput.press('g')
                time.sleep(0.1)
                pydirectinput.keyUp("ctrl")
                time.sleep(0.1)

                start_spell_timer = time.time()

            if time.time() - start_mob_clean_timer > clear_mobs_timer:  # once clear_mobs_timer seconds: cape then clear mobs for 10 second
                print("clearing mobs")

                pydirectinput.press('1')
                pydirectinput.keyDown('space')
                time.sleep(10)
                pydirectinput.keyUp('space')

                start_mob_clean_timer = time.time()

        else:
            print("No stones in range")
            pydirectinput.press('q')


game_automation(windows[0])

# Close all OpenCV windows
cv.destroyAllWindows()
