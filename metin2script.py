import pyautogui
import time
import keyboard
import pydirectinput


# def simulate_key_press():
#     pydirectinput.press('z')
#     time.sleep(0.3)
#
#
# if __name__ == "__main__":
#     while True:
#         simulate_key_press()

time.sleep(1)
pydirectinput.keyDown('space')

while True:
    pydirectinput.press('1')
    time.sleep(2)

