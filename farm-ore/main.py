import numpy as np
from PIL import ImageGrab
import cv2
import pytesseract
import time
import pyautogui
import pydirectinput

pytesseract.pytesseract.tesseract_cmd = r'F:\\Tesseract\tesseract.exe'
counter = 0
time1 = 0
time2 = 0
time3 = 0
time4 = 0
time5 = 0
time6 = 0
counterTotal1 = 0
counterTotal2 = 0
counterTotal3 = 0
counterTotal4 = 0
counterTotal5 = 0
counterTotal6 = 0
counterReusit1 = 0
counterReusit2 = 0
counterReusit3 = 0
counterReusit4 = 0
counterReusit5 = 0
counterReusit6 = 0

while True:

    # cap3
    cap3 = ImageGrab.grab(bbox=(1200, 540, 1500, 590))
    cap_arr3 = np.array(cap3)
    cap_arrResized3 = cv2.resize(cap_arr3, (600, 100))

    chat3 = pytesseract.image_to_string(cap_arrResized3)
    # verific si execut comenzile necesare
    if 'Punctele tale de exploatare au crescut' in chat3 and time.time() - time3 > 5:
        time3 = time.time()
        pyautogui.moveTo(1550, 250)
        pyautogui.click()
        pydirectinput.press('z')

        if 'Exploatarea a reusit' in chat3:
            counterReusit3 += 1
        counterTotal3 += 1

    # cap2
    cap2 = ImageGrab.grab(bbox=(650, 540, 950, 590))
    cap_arr2 = np.array(cap2)
    cap_arrResized2 = cv2.resize(cap_arr2, (600, 100))

    chat2 = pytesseract.image_to_string(cap_arrResized2)
    # verific si execut comenzile necesare
    if 'Punctele tale de exploatare au crescut' in chat2 and time.time() - time2 > 5:
        time2 = time.time()

        pyautogui.moveTo(1000, 250)
        pyautogui.click()
        pydirectinput.press('z')

        if 'Exploatarea a reusit' in chat2:
            counterReusit1 += 2
        counterTotal2 += 1

        pyautogui.moveTo(1550, 250)
        pyautogui.rightClick()

    # cap6
    cap6 = ImageGrab.grab(bbox=(1200, 990, 1500, 1040))
    cap_arr6 = np.array(cap6)
    cap_arrResized6 = cv2.resize(cap_arr6, (600, 100))

    chat6 = pytesseract.image_to_string(cap_arrResized6)
    print(chat6)
    # verific si execut comenzile necesare
    if 'Punctele tale de exploatare au crescut' in chat6 and time.time() - time6 > 5:
        time6 = time.time()
        # farm
        pyautogui.moveTo(1550, 650)
        pyautogui.click()
        pydirectinput.press('z')

        if 'Exploatarea a reusit' in chat6:
            counterReusit5 += 1
        counterTotal6 += 1
        # layout
        pyautogui.moveTo(1550, 250)
        pyautogui.rightClick()

    # cap1
    cap1 = ImageGrab.grab(bbox=(100, 540, 400, 590))
    cap_arr1 = np.array(cap1)
    cap_arrResized1 = cv2.resize(cap_arr1, (600, 100))

    chat1 = pytesseract.image_to_string(cap_arrResized1)
    # verific si execut comenzile necesare
    if 'Punctele tale de exploatare au crescut' in chat1 and time.time() - time1 > 5:
        # salvez momentul in care a detectat chatul pentru a astepta sa dispara chatul
        time1 = time.time()
        # farm
        pyautogui.moveTo(450, 250)
        pyautogui.click()
        pydirectinput.press('z')

        if 'Exploatarea a reusit' in chat1:
            counterReusit1 += 1
        counterTotal1 += 1
        # refac layout ul ecranelor
        pyautogui.moveTo(1000, 250)
        pyautogui.rightClick()
        pyautogui.moveTo(1550, 250)
        pyautogui.rightClick()

    # cap5
    cap5 = ImageGrab.grab(bbox=(650, 990, 950, 1040))
    cap_arr5 = np.array(cap5)
    cap_arrResized5 = cv2.resize(cap_arr5, (600, 100))

    chat5 = pytesseract.image_to_string(cap_arrResized5)
    # verific si execut comenzile necesare
    if 'Punctele tale de exploatare au crescut' in chat5 and time.time() - time5 > 5:
        time5 = time.time()
        # farm
        pyautogui.moveTo(1000, 650)
        pyautogui.click()
        pydirectinput.press('z')

        if 'Exploatarea a reusit' in chat5:
            counterReusit5 += 1
        counterTotal5 += 1

        # layout
        pyautogui.moveTo(1550, 650)
        pyautogui.rightClick()
        pyautogui.moveTo(1000, 250)
        pyautogui.rightClick()
        pyautogui.moveTo(1550, 250)
        pyautogui.rightClick()

    # cap4
    cap4 = ImageGrab.grab(bbox=(100, 990, 400, 1040))
    cap_arr4 = np.array(cap4)
    cap_arrResized4 = cv2.resize(cap_arr4, (600, 100))

    chat4 = pytesseract.image_to_string(cap_arrResized4)
    # verific si execut comenzile necesare
    if 'Punctele tale de exploatare au crescut' in chat4 and time.time() - time4 > 5:
        time4 = time.time()
        # farm
        pyautogui.moveTo(450, 650)
        pyautogui.click()
        pydirectinput.press('z')

        if 'Exploatarea a reusit' in chat4:
            counterReusit4 += 1
        counterTotal4 += 1
        # layout#
        pyautogui.moveTo(1000, 650)
        pyautogui.rightClick()
        pyautogui.moveTo(1550, 650)
        pyautogui.rightClick()
        pyautogui.moveTo(400, 250)
        pyautogui.rightClick()
        pyautogui.moveTo(1000, 250)
        pyautogui.rightClick()
        pyautogui.moveTo(1550, 250)
        pyautogui.rightClick()

    cv2.imshow("window6", cv2.cvtColor(cap_arrResized6, cv2.COLOR_BGR2RGB))
    # print(pytesseract.image_to_string(cap_arrResized6))

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
print('1st metin mined', counterTotal1, 'times')
print('2nd metin mined', counterTotal2, 'times')
print('3rd metin mined', counterTotal3, 'times')
print('4th metin mined', counterTotal4, 'times')
print('5th metin mined', counterTotal5, 'times')
print('6th metin mined', counterTotal6, 'times')
totalMinat = counterTotal1 + counterTotal2 + counterTotal3 + counterTotal4 + counterTotal5 + counterTotal6
totalReusit = counterReusit1 + counterReusit2 + counterReusit3 + counterReusit4 + counterReusit5 + counterReusit6
if totalMinat != 0:
    print('Total of:', totalMinat, 'of witch', totalReusit, 'succeded (', float(totalReusit / totalMinat) * 100, '% )')
else:
    print('U have to mine first xD')

cv2.destroyAllWindows()
