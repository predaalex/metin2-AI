import time

import pydirectinput

time.sleep(1)
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
time.sleep(0.5)
