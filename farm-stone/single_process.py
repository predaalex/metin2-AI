import datetime
import time
from multiprocessing import Process, Queue, Value, Lock

import cv2 as cv
import numpy as np
import pydirectinput
import pygetwindow
from PIL import ImageGrab


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


def get_stone_position_by_distance(window, frame, x_center, y_center, template, threshold, helper_points):
    frame = frame[100:-100, :]
    y_center -= 100
    result = cv.matchTemplate(frame, template, cv.TM_CCOEFF_NORMED)

    loc = np.where(result >= threshold)

    distances = {}

    for x_match, y_match in zip(*loc[::-1]):
        if x_match < window.width / 3:  # 1/3 of screen ( left )
            color = (0, 0, 0)
            x_click_offset = 55
        elif x_match < window.width * 2 / 3:  # 2/3 of screen ( middle )
            color = (125, 125, 125)
            x_click_offset = 40
        else:
            color = (255, 255, 255)  # 3/3 of screen ( right )
            x_click_offset = 30

        if y_match < window.height / 3:  # (top)
            y_click_offset = 45
        elif y_match < window.height * 2 / 3:  # (middle)
            y_click_offset = 55
        else:
            y_click_offset = 60  # (bottom)

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
        except Exception as e:
            
            print(f"[{datetime.datetime.now().hour:02}:{datetime.datetime.now().minute:02}:{datetime.datetime.now().second:02}]:"
                  f"Open window -> {e}")

    distances = dict(sorted(distances.items()))

    return distances


def get_stones_in_range(window, frame, x_center, y_center, template, threshold, radius, helper_points):
    frame = frame[100:-100, :]
    y_center -= 100
    result = cv.matchTemplate(frame, template, cv.TM_CCOEFF_NORMED)

    loc = np.where(result >= threshold)

    distances = {}

    for x_match, y_match in zip(*loc[::-1]):
        if x_match < window.width / 3:  # 1/3 of screen ( left )
            color = (0, 0, 0)
            x_click_offset = 55
        elif x_match < window.width * 2 / 3:  # 2/3 of screen ( middle )
            color = (125, 125, 125)
            x_click_offset = 40
        else:
            color = (255, 255, 255)  # 3/3 of screen ( right )
            x_click_offset = 30

        if y_match < window.height / 3:  # (top)
            y_click_offset = 45
        elif y_match < window.height * 2 / 3:  # (middle)
            y_click_offset = 55
        else:
            y_click_offset = 60  # (bottom)

        x_match += x_click_offset
        y_match += y_click_offset

        distance = int(np.sqrt((x_center - x_match) ** 2 + (y_center - y_match) ** 2))
        if distance > radius:
            distances[distance] = (x_match, y_match + 100)

        try:
            if helper_points:
                cv.circle(img=frame, center=(x_match, y_match),
                          radius=10, color=color, thickness=2)

                cv.circle(img=frame, center=(x_center, y_center),
                          radius=10, color=color, thickness=2)
        except Exception as e:
            
            print(f"[{datetime.datetime.now().hour:02}:{datetime.datetime.now().minute:02}:{datetime.datetime.now().second:02}]:"
                  f"Open window -> {e}")

    # distances = dict(sorted(distances.items()))

    return distances


def check_selected_metin(window, x_center, template_stone_check):
    frame = apply_color_filter(get_image(window))
    stone_hp_area = frame[40:100, x_center - 190: x_center + 190]
    # cv.imshow("stone_hp_area", stone_hp_area)
    # cv.waitKey(1)
    try:
        result = cv.matchTemplate(stone_hp_area, template_stone_check, cv.TM_CCOEFF_NORMED)
        return np.any(result > 0.9)

    except Exception as e:
        
        print(f"[{datetime.datetime.now().hour:02}:{datetime.datetime.now().minute:02}:{datetime.datetime.now().second:02}]:"
              f"Open game window -> {e}")
        return False


def select_window(window):
    pydirectinput.leftClick((window.left + window.right) // 2, window.top + 15)


def execute_command(window, message):
    select_window(window)
    pydirectinput.press('z')
    if message['command'] == "pressQ":
        pydirectinput.press('q', presses=3)
    elif message['command'] == "press1":
        pydirectinput.press('1')
    elif message['command'] == "pressEsc":
        pydirectinput.press('esc')
        time.sleep(0.5)
    elif message['command'] == 'press_right_click':
        pydirectinput.moveTo(window.left + message['x_click_pos'], window.top + message['y_click_pos'])
        pydirectinput.rightClick()
        time.sleep(0.2)
    elif message['command'] == 'press_left_click':
        pydirectinput.moveTo(window.left + message['x_click_pos'], window.top + message['y_click_pos'])
        pydirectinput.leftClick()
    elif message['command'] == 'select_stone':
        pydirectinput.moveTo(window.left + message['x_click_pos'], window.top + message['y_click_pos'])
        pydirectinput.leftClick()
        pydirectinput.press('q', presses=6)
        time.sleep(0.5)
    elif message['command'] == 'reset':
        # TODO: de modificat resetul in a se teleporta din noua in zona specifica
        #  aceasta abordare nu functioneaza pentru ca caracterul, chiar daca este blocat,
        #  doar misca camera in speranta de a apasa alta piatra metin pentru a incerca sa se deblocheze.

        template_next_button = cv.imread('resources/template_next_button.png', cv.IMREAD_GRAYSCALE)
        template_hwangyeon_teleport_name = cv.imread('resources/hwangyeon_teleport_name.png', cv.IMREAD_GRAYSCALE)
        template_center_zone_teleport = cv.imread("resources/center_zone.png", cv.IMREAD_GRAYSCALE)

        # press teleport ring
        pydirectinput.keyDown('alt')
        pydirectinput.press('1')
        pydirectinput.keyUp('alt')

        # press next 2 times for last page
        for _ in range(2):
            x_last_page, y_last_page = search_template_in_window(window, template_next_button)

            pydirectinput.leftClick(x_last_page, y_last_page)
            time.sleep(0.1)

        # press hwangyeon
        x_hwangyeon, y_hwangyeong = search_template_in_window(window, template_hwangyeon_teleport_name)
        pydirectinput.leftClick(x_hwangyeon, y_hwangyeong)
        time.sleep(0.1)

        # press center
        x_center, y_center = search_template_in_window(window, template_center_zone_teleport)
        pydirectinput.leftClick(x_center, y_center)
        time.sleep(1)
    elif message['command'] == 'chat_spam_last_message':
        time.sleep(0.1)
        pydirectinput.press('enter')
        time.sleep(0.1)
        pydirectinput.press('up')
        time.sleep(0.1)
        pydirectinput.press('enter')
        time.sleep(0.1)
        pydirectinput.press('enter')
        time.sleep(0.2)

    elif message['command'] == 'casting_spells':
        # unmount horse
        pydirectinput.keyDown("ctrl")
        pydirectinput.press('g')
        time.sleep(0.1)
        pydirectinput.keyUp("ctrl")
        time.sleep(0.5)

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
        time.sleep(0.2)

    elif message['command'] == 'clearing_mobs':
        pydirectinput.press('1')
        pydirectinput.keyDown('space')
        time.sleep(7)
        pydirectinput.keyUp('space')
        time.sleep(0.1)

    elif message['command'] == 'pressY':
        pydirectinput.press('y')
        time.sleep(0.1)

    elif message['command'] == 'press_send_item':
        pydirectinput.leftClick(message['biolog_send_item_x'], message['biolog_send_item_y'])
        time.sleep(0.2)
        pydirectinput.press('y')
        time.sleep(0.1)

    else:
        print(f"[{datetime.datetime.now().hour:02}:{datetime.datetime.now().minute:02}:{datetime.datetime.now().second:02}]:"
              f"Command does NOT exists!")


def apply_color_filter(img):
    mask = cv.inRange(img, 190, 255)
    res = cv.bitwise_and(img, img, mask=mask)
    return res


def search_template_in_window(window, template):

    frame = apply_color_filter(get_image(window))
    template = apply_color_filter(template)

    result = cv.matchTemplate(frame, template, cv.TM_CCOEFF_NORMED)

    loc = np.where(result >= 0.9)

    return loc[::-1][0][0] + window.left, loc[::-1][1][0] + window.top


def check_if_dead(window, revive_button):
    frame = get_image(window)

    result = cv.matchTemplate(frame, revive_button, cv.TM_CCOEFF_NORMED)
    
    if np.any(result > 0.5):
        loc = np.where(result >= 0.5)
        return True, loc[::-1][0][0], loc[::-1][1][0]
    else:
        return False, None, None


def worker():
    threshold = 0.8
    biolog_send_item_template = cv.imread("resources/biolog_send_item.png", cv.IMREAD_GRAYSCALE)
    revive_button = cv.imread("resources/revive_button.png", cv.IMREAD_GRAYSCALE)
    metin_counter = 0
    template = cv.imread("resources/template_hwangyeon.png", cv.IMREAD_GRAYSCALE)
    template_stone_check = cv.imread("resources/template_stone_hwangyeon.png", cv.IMREAD_GRAYSCALE)


    skill_timer = 50 * 60
    clear_mobs_timer = 99999
    reset_after = 10
    biolog_timer = 30 * 60 + 1

    helper_points = False
    debug_worker = False

    chat_spam_last_message = False
    make_biolog = False
    clear_mobs = False

    template_stone_check = apply_color_filter(template_stone_check)
    template = apply_color_filter(template)

    window = pygetwindow.getWindowsWithTitle('Zenaris')[0]
    start_spell_timer = time.time()
    start_mob_clean_timer = time.time()
    start_biolog_timer = time.time()
    while True:
        message = {
            'worker_id': 0,
        }

        # Get the window's position and size
        frame = get_image(window)
        # Get the center of window
        x_center, y_center = get_center(frame)

        # Check if any previous stones are selected
        if check_selected_metin(window, x_center, template_stone_check):
            if debug_worker:
                
                print(f"[{datetime.datetime.now().hour:02}:{datetime.datetime.now().minute:02}:{datetime.datetime.now().second:02}]:"
                      f"[Unselect stone]")

            message['command'] = 'pressEsc'
            execute_command(window, message)
            continue

        # Get the closest stone
        stones_in_range = get_stone_position_by_distance(window, apply_color_filter(get_image(window)),
                                                         x_center, y_center,
                                                         template, threshold, helper_points)

        # if there are 0 stones detected, pressQ and reset loop
        if len(stones_in_range) == 0:
            if debug_worker:
                print(f"[{datetime.datetime.now().hour:02}:{datetime.datetime.now().minute:02}:{datetime.datetime.now().second:02}]:"
                      f"[No stones detected!]")
            message['command'] = 'pressQ'
            execute_command(window, message)

            if debug_worker:
                print(f"[{datetime.datetime.now().hour:02}:{datetime.datetime.now().minute:02}:{datetime.datetime.now().second:02}]:"
                      f"[pressQ executed]")
            continue

        # Try to press all the stone in distances order and if couldn't pressQ any reset loop
        metin_selected = False
        for distance in stones_in_range:
            closest_x, closest_y = stones_in_range[distance]
            message['command'] = 'press_right_click'  # press right click to select stone
            message['x_click_pos'] = closest_x
            message['y_click_pos'] = closest_y
            execute_command(window, message)

            if check_selected_metin(window, x_center, template_stone_check):
                metin_selected = True
                break
            elif debug_worker:
                print(f"[{datetime.datetime.now().hour:02}:{datetime.datetime.now().minute:02}:{datetime.datetime.now().second:02}]:"
                      f"[Did NOT selected the metin]")

        if not metin_selected:
            if debug_worker:
                print(f"[{datetime.datetime.now().hour:02}:{datetime.datetime.now().minute:02}:{datetime.datetime.now().second:02}]:"
                      f"[Could NOT select any metin stones]")
            message['command'] = 'pressQ'
            execute_command(window, message)
            if debug_worker:
                print(f"[{datetime.datetime.now().hour:02}:{datetime.datetime.now().minute:02}:{datetime.datetime.now().second:02}]:"
                      f"[pressQ executed]")
            continue

        # left-click the validated stone
        message['command'] = 'select_stone'
        execute_command(window, message)

        # the stone was not destroyed under reset_after seconds,
        # so it changes camera position and begins the loop again
        break_loop = False
        time_while_attacking_metin = 0
        found_next_metin = False
        while check_selected_metin(window, x_center, template_stone_check):
            if time_while_attacking_metin == 0 and clear_mobs:
                # Call surrounding monsters
                message['command'] = 'press1'
                execute_command(window, message)

            # Check if next stone is if range
            stones_in_range = get_stones_in_range(window, apply_color_filter(get_image(window)),
                                                  x_center, y_center,
                                                  template, threshold, 100, helper_points)
            if len(stones_in_range) != 0:
                found_next_metin = True

            time_while_found = 0

            while len(stones_in_range) == 0 and not found_next_metin:

                # if there are 0 stones detected, pressQ
                if debug_worker:
                    print(f"[{datetime.datetime.now().hour:02}:{datetime.datetime.now().minute:02}:{datetime.datetime.now().second:02}]:"
                          f"[No future stones detected!]")

                message['command'] = 'pressQ'
                execute_command(window, message)
                if debug_worker:
                    print(
                        f"[{datetime.datetime.now().hour:02}:{datetime.datetime.now().minute:02}:{datetime.datetime.now().second:02}]:"
                        f"[pressQ executed]")
                stones_in_range = get_stones_in_range(window, apply_color_filter(get_image(window)),
                                                      x_center, y_center,
                                                      template, threshold, 100, helper_points)
                time_while_found += 0.5

                if len(stones_in_range) != 0:
                    found_next_metin = True

                if time_while_found > reset_after:
                    break

            time_while_found /= 1
            time_while_attacking_metin += time_while_found

            if time_while_attacking_metin % 5 == 0:
                print(f"[{datetime.datetime.now().hour:02}:{datetime.datetime.now().minute:02}:{datetime.datetime.now().second:02}]:"
                      f"[Stone hit for {time_while_attacking_metin}s]")

            time_while_attacking_metin += 1
            time.sleep(1)

            if time_while_attacking_metin > reset_after:

                is_dead, revive_button_x, revive_button_y = check_if_dead(window, revive_button)
                # Check if dead then revive
                if is_dead:
                    message['command'] = 'press_left_click'
                    message['x_click_pos'] = revive_button_x + 15
                    message['y_click_pos'] = revive_button_y + 5
                    execute_command(window, message)
                    time.sleep(1)
                    break_loop = True
                    break

                if debug_worker:
                    print(f"[{datetime.datetime.now().hour:02}:{datetime.datetime.now().minute:02}:{datetime.datetime.now().second:02}]:"
                          f"[Restart because timer expired]")
                message['command'] = 'reset'
                execute_command(window, message)

                break_loop = True
                break
        if break_loop:
            continue

        print(f"[{datetime.datetime.now().hour:02}:{datetime.datetime.now().minute:02}:{datetime.datetime.now().second:02}]:"
              f"[Stone destroyed]")
        metin_counter += 1

        # After stone was destroyed, write last message in chat
        if chat_spam_last_message and metin_counter % 5 == 0:
            message['command'] = 'chat_spam_last_message'
            execute_command(window, message)

        if time.time() - start_spell_timer > skill_timer:  # After expiration time, spells are casted again
            if debug_worker:
                
                print(f"[{datetime.datetime.now().hour:02}:{datetime.datetime.now().minute:02}:{datetime.datetime.now().second:02}]:"
                      f"[casting spells]")
            message['command'] = 'casting_spells'
            execute_command(window, message)

            start_spell_timer = time.time()

        # once clear_mobs_timer seconds: cape then clear mobs for 10 second
        if time.time() - start_mob_clean_timer > clear_mobs_timer:  
            if debug_worker:
                
                print(f"[{datetime.datetime.now().hour:02}:{datetime.datetime.now().minute:02}:{datetime.datetime.now().second:02}]:"
                      f"[clearing mob]")
            message['command'] = 'clearing_mobs'
            execute_command(window, message)

            start_mob_clean_timer = time.time()
            
        # once biolog_timer open biolog window and press send_item
        if make_biolog and time.time() - start_biolog_timer > biolog_timer:  
            if debug_worker:
                
                print(f"[{datetime.datetime.now().hour:02}:{datetime.datetime.now().minute:02}:{datetime.datetime.now().second:02}]:"
                      f"[solve biolog]")

            # open biolog window
            message['command'] = 'pressY'
            execute_command(window, message)

            # search send_item and press
            try:
                biolog_send_item_x, biolog_send_item_y = search_template_in_window(window, get_image(window),
                                                                                   biolog_send_item_template)
                message['command'] = 'press_send_item'
                message['biolog_send_item_x'] = biolog_send_item_x + 15
                message['biolog_send_item_y'] = biolog_send_item_y + 15
                execute_command(window, message)
            except Exception as e:
                
                print(f"[{datetime.datetime.now().hour:02}:{datetime.datetime.now().minute:02}:{datetime.datetime.now().second:02}]:"
                      f"[ERROR!: solve biolog] -> {e}")
                message['command'] = 'pressY'
                execute_command(window, message)

            start_biolog_timer = time.time()

        print(f"[{datetime.datetime.now().hour:02}:{datetime.datetime.now().minute:02}:{datetime.datetime.now().second:02}]:"
              f"[timer skills: {time.time() - start_spell_timer:.1f} / {skill_timer} s]")
        if clear_mobs:
            
            print(f"[{datetime.datetime.now().hour:02}:{datetime.datetime.now().minute:02}:{datetime.datetime.now().second:02}]:"
                  f"[timer mobi: {time.time() - start_mob_clean_timer:.1f} / {clear_mobs_timer} s]")
        if make_biolog:
            
            print(f"[{datetime.datetime.now().hour:02}:{datetime.datetime.now().minute:02}:{datetime.datetime.now().second:02}]:"
                  f"[timer biolog: {time.time() - start_biolog_timer:.1f} / {biolog_timer} s]")



if __name__ == '__main__':
    worker()
