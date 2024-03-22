import datetime
import time
from multiprocessing import Process, Queue, Value, Lock

import cv2 as cv
import numpy as np
import pydirectinput
import pygetwindow
from PIL import ImageGrab

window = pygetwindow.getWindowsWithTitle("Rust")[0]

time.sleep(0.5)
pydirectinput.press('e')
buys = 21

for buy_index in range(buys):

    # amount coords
    pydirectinput.leftClick(window.left + 2550, window.top + 1235)
    pydirectinput.press('1', presses=2)

    # buy coords
    pydirectinput.moveTo(window.left + 2540, window.top + 1180)
    pydirectinput.leftClick()

    print(f"Buy {buy_index} / {buys}")
    time.sleep(2.8)

print("FINISH")