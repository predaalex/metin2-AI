import pyautogui
import time
import keyboard
import pydirectinput


def simulate_key_press():
    toggle = True
    while True:
        # pydirectinput.keyDown('space')
        if keyboard.is_pressed('q'):
            break
        if keyboard.is_pressed('e'):
            toggle = -toggle
        if toggle:
            pydirectinput.press('z')
        # pydirectinput.press('1')
        time.sleep(0.1)
    # pydirectinput.keyUp('space')


if __name__ == "__main__":
    simulate_key_press()
