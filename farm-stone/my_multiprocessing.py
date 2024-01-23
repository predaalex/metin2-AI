import datetime
import time
from multiprocessing import Process, Queue, Value, Lock

import cv2 as cv
import numpy as np
import pydirectinput
import pygetwindow
import pygetwindow as gw
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
                  f"Open {window_title} window -> {e}")

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
                  f"Open {window_title} window -> {e}")

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
    if message['command'] == "pressQ":
        pydirectinput.press('q')
    elif message['command'] == "press1":
        pydirectinput.press('1')
    elif message['command'] == "pressEsc":
        pydirectinput.press('esc')
    elif message['command'] == 'press_right_click':
        pydirectinput.moveTo(window.left + message['x_click_pos'], window.top + message['y_click_pos'])
        pydirectinput.rightClick()
    elif message['command'] == 'press_left_click':
        pydirectinput.moveTo(window.left + message['x_click_pos'], window.top + message['y_click_pos'])
        pydirectinput.leftClick()
    elif message['command'] == 'select_stone':
        pydirectinput.moveTo(window.left + message['x_click_pos'], window.top + message['y_click_pos'])
        pydirectinput.leftClick()
        pydirectinput.press('q', presses=10)
    elif message['command'] == 'reset':
        pydirectinput.press('z')
        time.sleep(0.1)
        # pydirectinput.press('esc')
        # time.sleep(0.1)
        pydirectinput.press('q', presses=10)
        time.sleep(0.1)
    elif message['command'] == 'chat_spam_last_message':
        time.sleep(0.1)
        pydirectinput.press('enter')
        time.sleep(0.1)
        pydirectinput.press('up')
        time.sleep(0.1)
        pydirectinput.press('enter')
        time.sleep(0.1)
        pydirectinput.press('enter')
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
    elif message['command'] == 'clearing_mobs':
        pydirectinput.press('1')
        pydirectinput.keyDown('space')
        time.sleep(7)
        pydirectinput.keyUp('space')
    elif message['command'] == 'pick_up':
        pydirectinput.press('z')
    elif message['command'] == 'pressY':
        pydirectinput.press('y')
    elif message['command'] == 'press_send_item':
        pydirectinput.leftClick(message['biolog_send_item_x'], message['biolog_send_item_y'])
        time.sleep(0.2)
        pydirectinput.press('y')
    else:
        print(f"[{datetime.datetime.now().hour:02}:{datetime.datetime.now().minute:02}:{datetime.datetime.now().second:02}]:"
              f"Command does NOT exists!")


def apply_color_filter(img):
    mask = cv.inRange(img, 190, 255)
    res = cv.bitwise_and(img, img, mask=mask)
    return res


def search_biolog_send_item(window, frame, biolog_send_item_template):
    result = cv.matchTemplate(frame, biolog_send_item_template, cv.TM_CCOEFF_NORMED)

    loc = np.where(result >= 0.9)

    return loc[::-1][0][0], loc[::-1][1][0]


def check_if_dead(window, revive_button):
    frame = get_image(window)

    result = cv.matchTemplate(frame, revive_button, cv.TM_CCOEFF_NORMED)
    
    if np.any(result > 0.5):
        loc = np.where(result >= 0.5)
        return True, loc[::-1][0][0], loc[::-1][1][0]
    else:
        return False, None, None


def worker(queue, lock, worker_id, stop_signal):
    threshold = 0.8
    biolog_send_item_template = cv.imread("resources/biolog_send_item.png", cv.IMREAD_GRAYSCALE)
    revive_button = cv.imread("resources/revive_button.png", cv.IMREAD_GRAYSCALE)
    metin_counter = 0
    if worker_id == 0:
        template = cv.imread("resources/template_hwangyeon.png", cv.IMREAD_GRAYSCALE)
        template_stone_check = cv.imread("resources/template_stone_hwangyeon.png", cv.IMREAD_GRAYSCALE)

        skill_timer = 50 * 60
        clear_mobs_timer = 99999
        reset_after = 15
        biolog_timer = 5 * 60 + 1

        helper_points = False
        debug_worker = False

        chat_spam_last_message = False
        make_biolog = False
        clear_mobs = False
    else:
        template = cv.imread("resources/template_hwangyeon.png", cv.IMREAD_GRAYSCALE)
        template_stone_check = cv.imread("resources/template_stone_hwangyeon.png", cv.IMREAD_GRAYSCALE)

        skill_timer = 20 * 60
        clear_mobs_timer = 99999
        reset_after = 35
        biolog_timer = 10 * 60 + 1

        helper_points = False
        debug_worker = False

        chat_spam_last_message = False
        make_biolog = True
        clear_mobs = False

    template_stone_check = apply_color_filter(template_stone_check)
    template = apply_color_filter(template)

    window = pygetwindow.getWindowsWithTitle('Zenaris')[worker_id]
    start_spell_timer = time.time()
    start_mob_clean_timer = time.time()
    start_biolog_timer = time.time()
    while stop_signal.value != 1:
        message = {
            'worker_id': worker_id,
        }

        # Get the window's position and size
        frame = get_image(window)
        # Get the center of window
        x_center, y_center = get_center(frame)

        # Check if any previous stones are selected
        if check_selected_metin(window, x_center, template_stone_check):
            if debug_worker:
                
                print(f"[{datetime.datetime.now().hour:02}:{datetime.datetime.now().minute:02}:{datetime.datetime.now().second:02}]:"
                      f"Worker {worker_id}: [Unselect stone]")

            message['command'] = 'pressEsc'
            lock.acquire()
            queue.put(message)

            time.sleep(0.5)
            continue

        # Get the closest stone
        stones_in_range = get_stone_position_by_distance(window, apply_color_filter(get_image(window)),
                                                         x_center, y_center,
                                                         template, threshold, helper_points)

        # if there are 0 stones detected, pressQ and reset loop
        if len(stones_in_range) == 0:
            if debug_worker:
                
                print(f"[{datetime.datetime.now().hour:02}:{datetime.datetime.now().minute:02}:{datetime.datetime.now().second:02}]:"
                      f"Worker {worker_id}: [No stones detected!]")
            message['command'] = 'pressQ'
            lock.acquire()
            queue.put(message)

            time.sleep(0.5)
            continue

        # Try to press all the stone in distances order and if couldn't pressQ any reset loop
        metin_selected = False
        for distance in stones_in_range:
            closest_x, closest_y = stones_in_range[distance]
            message['command'] = 'press_right_click'  # press right click to select stone
            message['x_click_pos'] = closest_x
            message['y_click_pos'] = closest_y
            lock.acquire()
            queue.put(message)

            time.sleep(1)
            if check_selected_metin(window, x_center, template_stone_check):
                metin_selected = True
                break
            elif debug_worker:
                
                print(f"[{datetime.datetime.now().hour:02}:{datetime.datetime.now().minute:02}:{datetime.datetime.now().second:02}]:"
                      f"Worker {worker_id}: [Did NOT selected the metin]")

        if not metin_selected:
            if debug_worker:
                
                print(f"[{datetime.datetime.now().hour:02}:{datetime.datetime.now().minute:02}:{datetime.datetime.now().second:02}]:"
                      f"Worker {worker_id}: [Could NOT select any metin stones]")
            message['command'] = 'pressQ'
            lock.acquire()
            queue.put(message)
            time.sleep(0.5)
            continue

        # left-click the validated stone
        message['command'] = 'select_stone'
        lock.acquire()
        queue.put(message)
        time.sleep(2)

        # the stone was not destroyed under reset_after seconds,
        # so it changes camera position and begins the loop again
        break_loop = False
        time_while_attacking_metin = 0
        found_next_metin = False
        while check_selected_metin(window, x_center, template_stone_check):
            if time_while_attacking_metin == 0 and clear_mobs:
                # Call surrounding monsters
                message['command'] = 'press1'
                lock.acquire()
                queue.put(message)
                time.sleep(0.5)

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
                          f"Worker {worker_id}: [No stones detected!]")
                message['command'] = 'pressQ'
                lock.acquire()
                queue.put(message)
                time.sleep(0.5)
                stones_in_range = get_stones_in_range(window, apply_color_filter(get_image(window)),
                                                      x_center, y_center,
                                                      template, threshold, 100, helper_points)
                time_while_found += 0.5

                if len(stones_in_range) != 0:
                    found_next_metin = True
                if time_while_found > reset_after:
                    time.sleep(0.5)
                    break

            time_while_found /= 1
            time_while_attacking_metin += time_while_found

            if time_while_attacking_metin % 5 == 0:
                
                print(f"[{datetime.datetime.now().hour:02}:{datetime.datetime.now().minute:02}:{datetime.datetime.now().second:02}]:"
                      f"Worker {worker_id}: [Stone hit for {time_while_attacking_metin}s]")
            time_while_attacking_metin += 1
            time.sleep(1)
            if time_while_attacking_metin > reset_after:

                is_dead, revive_button_x, revive_button_y = check_if_dead(window, revive_button)
                # Check if dead then revive
                if is_dead:
                    time.sleep(10)
                    message['command'] = 'press_left_click'
                    message['x_click_pos'] = revive_button_x + 15
                    message['y_click_pos'] = revive_button_y + 5
                    lock.acquire()
                    queue.put(message)
                    time.sleep(1)
                    break_loop = True
                    break

                if debug_worker:
                    print(f"[{datetime.datetime.now().hour:02}:{datetime.datetime.now().minute:02}:{datetime.datetime.now().second:02}]:"
                          f"Worker {worker_id}: [Restart because timer expired]")
                message['command'] = 'reset'
                lock.acquire()
                queue.put(message)

                break_loop = True
                time.sleep(0.5)
                break
        if break_loop:
            continue

        print(f"[{datetime.datetime.now().hour:02}:{datetime.datetime.now().minute:02}:{datetime.datetime.now().second:02}]:"
              f"Worker {worker_id}: [Stone destroyed]")
        metin_counter += 1

        message['command'] = 'pick_up'
        lock.acquire()
        queue.put(message)

        time.sleep(0.5)
        # After stone was destroyed, write last message in chat
        if chat_spam_last_message and metin_counter % 5 == 0:
            message['command'] = 'chat_spam_last_message'
            lock.acquire()
            queue.put(message)
            time.sleep(0.5)

        if time.time() - start_spell_timer > skill_timer:  # After expiration time, spells are casted again
            if debug_worker:
                
                print(f"[{datetime.datetime.now().hour:02}:{datetime.datetime.now().minute:02}:{datetime.datetime.now().second:02}]:"
                      f"Worker {worker_id}: [casting spells]")
            message['command'] = 'casting_spells'
            lock.acquire()
            queue.put(message)
            time.sleep(0.5)

            start_spell_timer = time.time()

        # once clear_mobs_timer seconds: cape then clear mobs for 10 second
        if time.time() - start_mob_clean_timer > clear_mobs_timer:  
            if debug_worker:
                
                print(f"[{datetime.datetime.now().hour:02}:{datetime.datetime.now().minute:02}:{datetime.datetime.now().second:02}]:"
                      f"Worker {worker_id}: [clearing mob]")
            message['command'] = 'clearing_mobs'
            lock.acquire()
            queue.put(message)
            time.sleep(0.5)

            start_mob_clean_timer = time.time()
            
        # once biolog_timer open biolog window and press send_item
        if make_biolog and time.time() - start_biolog_timer > biolog_timer:  
            if debug_worker:
                
                print(f"[{datetime.datetime.now().hour:02}:{datetime.datetime.now().minute:02}:{datetime.datetime.now().second:02}]:"
                      f"Worker {worker_id}: [solve biolog]")

            # open biolog window
            message['command'] = 'pressY'
            lock.acquire()
            queue.put(message)
            time.sleep(0.5)

            # search send_item and press
            try:
                biolog_send_item_x, biolog_send_item_y = search_biolog_send_item(window, get_image(window),
                                                                                 biolog_send_item_template)
                message['command'] = 'press_send_item'
                message['biolog_send_item_x'] = biolog_send_item_x + window.left + 15
                message['biolog_send_item_y'] = biolog_send_item_y + window.top + 15
                lock.acquire()
                queue.put(message)
                time.sleep(0.2)
            except Exception as e:
                
                print(f"[{datetime.datetime.now().hour:02}:{datetime.datetime.now().minute:02}:{datetime.datetime.now().second:02}]:"
                      f"Worker {worker_id}: [ERROR!: solve biolog] -> {e}")
                message['command'] = 'pressY'
                lock.acquire()
                queue.put(message)
                time.sleep(0.2)

            message['command'] = 'pressQ'
            queue.put(message)
            lock.acquire()
            time.sleep(0.2)

            start_biolog_timer = time.time()

        print(f"[{datetime.datetime.now().hour:02}:{datetime.datetime.now().minute:02}:{datetime.datetime.now().second:02}]:"
              f"Worker {worker_id}: [timer skills: {time.time() - start_spell_timer:.1f} / {skill_timer} s]")
        if clear_mobs:
            
            print(f"[{datetime.datetime.now().hour:02}:{datetime.datetime.now().minute:02}:{datetime.datetime.now().second:02}]:"
                  f"Worker {worker_id}: [timer mobi: {time.time() - start_mob_clean_timer:.1f} / {clear_mobs_timer} s]")
        if make_biolog:
            
            print(f"[{datetime.datetime.now().hour:02}:{datetime.datetime.now().minute:02}:{datetime.datetime.now().second:02}]:"
                  f"Worker {worker_id}: [timer biolog: {time.time() - start_biolog_timer:.1f} / {biolog_timer} s]")


def master(queue, lock, stop_signal, window_title):
    try:
        
        print(f"[{datetime.datetime.now().hour:02}:{datetime.datetime.now().minute:02}:{datetime.datetime.now().second:02}]:"
              f"Master process started")
        windows = pygetwindow.getWindowsWithTitle(window_title)
        while True:
            if not queue.empty():
                message = queue.get()
                
                print(f"[{datetime.datetime.now().hour:02}:{datetime.datetime.now().minute:02}:{datetime.datetime.now().second:02}]:"
                      f"Executing command from worker {message['worker_id']}: {message['command']}")
                execute_command(window=windows[message['worker_id']], message=message)
                lock.release()
            else:
                time.sleep(0.1)  # Sleep to prevent high CPU usage
    except KeyboardInterrupt:
        
        print(f"[{datetime.datetime.now().hour:02}:{datetime.datetime.now().minute:02}:{datetime.datetime.now().second:02}]:"
              f"Stopping all processes.")
        stop_signal.value = 1


if __name__ == '__main__':
    command_queue = Queue()
    lock = Lock()
    num_workers = 1
    stop_signal = Value('i', 0)
    window_title = "Zenaris"
    windows = gw.getWindowsWithTitle(window_title)
    num_windows = len(windows)

    if num_windows < num_workers:
        
        print(f"[{datetime.datetime.now().hour:02}:{datetime.datetime.now().minute:02}:{datetime.datetime.now().second:02}]:"
              f"Not enough game windows open")
        raise SystemExit

    master_process = Process(target=master, args=(command_queue, lock, stop_signal, window_title))
    master_process.start()

    worker_processes = []
    for worker_id in range(num_workers):
        p = Process(target=worker, args=(command_queue, lock, worker_id, stop_signal))
        p.start()
        worker_processes.append(p)

    for wp in worker_processes:
        wp.join()

    master_process.terminate()
    master_process.join()
