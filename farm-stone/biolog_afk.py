from multiprocessing import Process, Queue, Value, Event, Lock
import time
import cv2 as cv
import numpy as np
import pygetwindow
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
    # screenshot = cv.resize(screenshot, (0, 0), fx=0.5, fy=0.5)

    return screenshot


def select_window(window):
    pydirectinput.leftClick((window.left + window.right) // 2, window.top + 15)


def execute_command(lock, window, message):
    select_window(window)
    if message['command'] == "pressQ":
        pydirectinput.press('q')
    elif message['command'] == "pressY":
        pydirectinput.press('y')
    elif message['command'] == 'drag_biolog_window_to_center':
        pydirectinput.moveTo(message['current_biolog_window_x'], message['current_biolog_window_y'], duration=0.1)
        pydirectinput.mouseDown(button='left')
        pydirectinput.moveTo(window.centerx, window.centery, duration=0.1)
        pydirectinput.mouseUp(button='left')
    elif message['command'] == 'press_send_item':
        pydirectinput.leftClick(message['biolog_send_item_x'], message['biolog_send_item_y'])
        time.sleep(0.5)
        pydirectinput.press('y')
    else:
        print("Command does NOT exists!")


def apply_color_filter(img):
    mask = cv.inRange(img, 190, 255)
    res = cv.bitwise_and(img, img, mask=mask)
    return res


def seach_biolog_window(window, frame, biolog_window_template):
    result = cv.matchTemplate(frame, biolog_window_template, cv.TM_CCOEFF_NORMED)
    loc = np.where(result >= 0.9)
    return loc[::-1][0][0], loc[::-1][1][0]


def search_biolog_send_item(window, frame, biolog_send_item_template):
    # frame = frame[frame.shape[0] // 2:frame.shape[0] // 2 + 150, frame.shape[1] // 2:frame.shape[1] // 2 + 300]

    result = cv.matchTemplate(frame, biolog_send_item_template, cv.TM_CCOEFF_NORMED)

    loc = np.where(result >= 0.9)

    return loc[::-1][0][0], loc[::-1][1][0]


def worker(queue, lock, worker_id, stop_signal):
    chat_spam_last_message = False
    biolog_send_item_template = cv.imread("resources/biolog_send_item.png", cv.IMREAD_GRAYSCALE)

    window = pygetwindow.getWindowsWithTitle('Zenaris')[worker_id]
    while stop_signal.value != 1:
        message = {
            'worker_id': worker_id,
        }

        print(f"Worker {worker_id}: [solve biolog]")

        # open biolog window
        message['command'] = 'pressY'
        lock.acquire()
        queue.put(message)
        time.sleep(0.5)

        # search send_item and press
        biolog_send_item_x, biolog_send_item_y = search_biolog_send_item(window, get_image(window),
                                                                         biolog_send_item_template)
        message['command'] = 'press_send_item'
        message['biolog_send_item_x'] = biolog_send_item_x + window.left + 15
        message['biolog_send_item_y'] = biolog_send_item_y + window.top + 15
        lock.acquire()
        queue.put(message)
        time.sleep(0.5)

        message['command'] = 'pressQ'
        queue.put(message)
        lock.acquire()

        time.sleep(30)


def master(queue, lock, stop_signal, window_title):
    try:
        print("Master process started")
        windows = pygetwindow.getWindowsWithTitle(window_title)
        while True:
            if not queue.empty():
                message = queue.get()
                print(f"Executing command from worker {message['worker_id']}: {message['command']}")
                execute_command(lock, window=windows[message['worker_id']], message=message)
                lock.release()
            else:
                time.sleep(0.1)  # Sleep to prevent high CPU usage
    except KeyboardInterrupt:
        print("Stopping all processes.")
        stop_signal.value = 1


if __name__ == '__main__':
    command_queue = Queue()
    lock = Lock()
    num_workers = 2
    stop_signal = Value('i', 0)
    window_title = "Zenaris"
    windows = gw.getWindowsWithTitle(window_title)
    num_windows = len(windows)

    if num_windows < num_workers:
        print("Not enought game windows open")
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
