from multiprocessing import Process, Queue, Value, Event
# import multiprocessing
import time
import cv2 as cv
import numpy as np
import pygetwindow
import pygetwindow as gw
import pydirectinput
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
    global x_click_offset, y_click_offset
    frame = frame[100:-100, :]
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


def check_selected_metin(frame, x_center, template_stone_check):
    stone_hp_area = frame[:100, x_center - 190: x_center + 190]

    try:
        result = cv.matchTemplate(stone_hp_area, template_stone_check, cv.TM_CCOEFF_NORMED)
        return np.any(result > 0.9)
    except:
        print("Open game window")
        return False


def print_circles(frame, closest_x, closest_y, x_center, y_center, helper_points):
    color = (0, 0, 0)

    try:
        if helper_points:
            cv.circle(img=frame, center=(closest_x, closest_y),
                      radius=20, color=color, thickness=2)

            cv.circle(img=frame, center=(x_center, y_center),
                      radius=20, color=color, thickness=2)
    except:
        print(f"Open {window_title} window")


def select_window(window):
    pydirectinput.leftClick(window.left + 50, window.top + 25)


def execute_command(event, window, message):
    select_window(window)
    if message['command'] == "pressQ":
        pydirectinput.press('q')
    elif message['command'] == 'select_stone':
        pydirectinput.moveTo(window.left + message['x_stone_pos'], window.top + message['y_stone_pos'])
        pydirectinput.rightClick()
    elif message['command'] == 'press_left_click':
        pydirectinput.leftClick(window.left + message['x_click_pos'], window.top + message['y_click_pos'])
    elif message['command'] == 'reset':
        pydirectinput.press('z')
        pydirectinput.press('esc')
        pydirectinput.press('q', presses=10)
    elif message['command'] == 'chat_spam_last_message':
        time.sleep(0.5)
        pydirectinput.press('enter')
        time.sleep(0.5)
        pydirectinput.press('up')
        time.sleep(0.5)
        pydirectinput.press('enter')
        time.sleep(0.5)
        pydirectinput.press('enter')
        time.sleep(0.5)
    elif message['command'] == 'casting_spells':
        # unmount horse
        pydirectinput.keyDown("ctrl")
        pydirectinput.press('g')
        time.sleep(0.5)
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
        time.sleep(0.5)
        pydirectinput.keyUp("ctrl")
        time.sleep(0.5)
    elif message['command'] == 'clearing_mobs':
        pydirectinput.press('1')
        pydirectinput.keyDown('space')
        time.sleep(10)
        pydirectinput.keyUp('space')
    else:
        print("Command does NOT exists!")
    event.set()


def worker(queue, event, worker_id, stop_signal):
    helper_points = False
    chat_spam_last_message = False
    threshold = 0.8
    skill_timer = 10 * 60
    clear_mobs_timer = 600
    reset_after = 90
    message = {
        'worker_id': worker_id,
    }
    if worker_id == 0:
        template = cv.imread("resources/template.png", cv.IMREAD_GRAYSCALE)
        template_stone_check = cv.imread("resources/template_stone_check.png", cv.IMREAD_GRAYSCALE)
    else:
        template = cv.imread("resources/template2.png", cv.IMREAD_GRAYSCALE)
        template_stone_check = cv.imread("resources/template_stone_check2.png", cv.IMREAD_GRAYSCALE)

    window = pygetwindow.getWindowsWithTitle('Zenaris')[worker_id]
    start_spell_timer = time.time()
    start_mob_clean_timer = time.time()
    while stop_signal.value != 1:
        # Get the window's position and size
        frame = get_image(window)
        # Get the center of window
        x_center, y_center = get_center(frame)

        # Get the closest stone
        distances_sorted = get_stone_position_by_distance(window, frame, x_center, y_center, template, threshold,
                                                          helper_points)
        iterator = iter(distances_sorted)
        closest_dist = next(iterator, None)

        if distances_sorted:
            closest_x, closest_y = distances_sorted[closest_dist]

            # Right click on stone
            message['command'] = 'select_stone'
            message['x_stone_pos'] = closest_x
            message['y_stone_pos'] = closest_y
            queue.put(message)
            event.wait()
            event.clear()
            time.sleep(0.5)

            # check if the right metin was clicked
            try:
                while not check_selected_metin(get_image(window), x_center, template_stone_check):
                    closest_dist = next(iterator, None)
                    closest_x, closest_y = distances_sorted[closest_dist]
                    message['command'] = 'select_stone'
                    message['x_stone_pos'] = closest_x
                    message['y_stone_pos'] = closest_y
                    queue.put(message)
                    event.wait()
                    event.clear()
                    time.sleep(0.5)
                    print(f"Worker {worker_id}: [Did NOT selected the metin]")
            except:
                print(f"Worker {worker_id}: [Could NOT select any metin stones]")
                message['command'] = 'pressQ'
                queue.put(message)
                event.wait()
                event.clear()
                time.sleep(0.5)

            # left-click the validated stone
            message['command'] = 'press_left_click'
            message['x_click_pos'] = closest_x
            message['y_click_pos'] = closest_y
            queue.put(message)
            event.wait()
            event.clear()

            # the stone was not destroyed under 30 seconds,
            # so it changes camera position and begins the loop again
            break_loop = False
            i = 0
            while check_selected_metin(get_image(window), x_center, template_stone_check):
                print(f"Worker {worker_id}: [Stone hit for {i}s]")
                i += 1
                time.sleep(1)
                if i > reset_after:
                    print(f"Worker {worker_id}: [Restart because timer expired]")
                    message['command'] = 'reset'
                    queue.put(message)
                    event.wait()
                    event.clear()
                    break_loop = True
                    time.sleep(0.5)
                    break
            if break_loop:
                continue

            print(f"Worker {worker_id}: [Stone destroyed]")
            print(f"Worker {worker_id}: [timer mobi: {time.time() - start_mob_clean_timer}]")
            print(f"Worker {worker_id}: [timer mobi: {time.time() - start_spell_timer}]")

            pydirectinput.press('z')

            # After stone was destroyed, write last message in chat
            if chat_spam_last_message:
                message['command'] = 'chat_spam_last_message'
                queue.put(message)
                event.wait()
                event.clear()

            if time.time() - start_spell_timer > skill_timer:  # After expiration time, spells are casted again
                print(f"Worker {worker_id}: [casting spells]")
                message['command'] = 'casting_spells'
                queue.put(message)
                event.wait()
                event.clear()

                start_spell_timer = time.time()

            if time.time() - start_mob_clean_timer > clear_mobs_timer:  # once clear_mobs_timer seconds: cape then clear mobs for 10 second
                print(f"Worker {worker_id}: [clearing mob]")
                message['command'] = 'clearing_mobs'
                queue.put(message)
                event.wait()
                event.clear()

                start_mob_clean_timer = time.time()

        else:
            print(f"Worker {worker_id}: [No stones in range]")
            message['command'] = 'pressQ'
            queue.put(message)
            event.wait()
            event.clear()
            time.sleep(0.5)


def master(queue, event, stop_signal, window_title):
    try:
        print("Master process started")
        windows = pygetwindow.getWindowsWithTitle(window_title)
        while True:
            if not queue.empty():
                message = queue.get()
                print(f"Executing command from worker{message['worker_id']}: {message['command']}")
                execute_command(event, window=windows[message['worker_id']], message=message)
            else:
                time.sleep(0.5)  # Sleep to prevent high CPU usage
    except KeyboardInterrupt:
        print("Stopping all processes.")
        stop_signal.value = 1


if __name__ == '__main__':
    command_queue = Queue()
    event = Event()
    event.clear()
    num_workers = 1
    stop_signal = Value('i', 0)
    window_title = "Zenaris"

    windows = gw.getWindowsWithTitle(window_title)
    num_windows = len(windows)

    if num_windows < num_workers:
        print("Not enought game windows open")
        raise SystemExit

    master_process = Process(target=master, args=(command_queue, event, stop_signal, window_title))
    master_process.start()

    worker_processes = []
    for worker_id in range(num_workers):
        p = Process(target=worker, args=(command_queue, event, worker_id, stop_signal))
        p.start()
        worker_processes.append(p)

    for wp in worker_processes:
        wp.join()

    master_process.terminate()
    master_process.join()
