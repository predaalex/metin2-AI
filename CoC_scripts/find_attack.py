import time

import cv2 as cv
import pydirectinput
import pygetwindow
import easyocr

import opencv_utils as utils
import re


def extract_text_from_image(image,
                          crop_rect=(135, 0, 270, 250),
                          scale=4,
                          reader=None):
    """
    Args:
      image      : full BGR image (numpy array)
      crop_rect  : (y1, x1, y2, x2) rectangle of the 3-line panel
      scale      : upsampling factor before binarization
      reader     : an EasyOCR reader instance already created
    Returns:
      List of three strings, e.g. ['548663','717468','5773']
    """
    y1, x1, y2, x2 = crop_rect
    # 1) Crop to the number panel
    roi = image[y1:y2, x1:x2]

    # 2) Pre-process
    # upscale so small digits become legible
    image = cv.resize(roi, None,
                     fx=scale, fy=scale,
                     interpolation=cv.INTER_CUBIC)

    # denoise a bit
    image = cv.GaussianBlur(image, (5,5), 0)

    # Otsu threshold + invert so text is white on black
    _, bw = cv.threshold(image, 0, 255,
                        cv.THRESH_BINARY_INV + cv.THRESH_OTSU)

    # morph open to remove tiny speckles
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (3,3))
    clean = cv.morphologyEx(bw, cv.MORPH_OPEN, kernel, iterations=1)
    # invert back: black text on white background
    clean = cv.bitwise_not(clean)


    # 3) Split into three equal-height bands
    h = clean.shape[0]
    bands = [ clean[int(i*h/3):int((i+1)*h/3), :] for i in range(3) ]

    # 4) OCR each band with digits-only
    nums = []
    for band in bands:
        txts = reader.readtext(band,
                               detail=0,
                               text_threshold=0.3,
                               allowlist='0123456789')
        # sometimes EasyOCR will return ['5','4','8','6','6','3']…
        # so join and strip out non-digits just in case:
        joined = ''.join(txts)
        digit_str = ''.join([c for c in joined if c.isdigit()])
        nums.append(int(digit_str))

    return nums


def extract_resources(image, reader):
    text = extract_text_from_image(image, reader=reader)

    resources = {
        "gold": text[0],
        "elixir": text[1],
        "dark elixir": text[2]
    }

    return resources


def printResources(numbers):
    # Find the largest number to know how wide the column should be
    width = len(f"{max(numbers.values()):,}")
    for resource, amount in numbers.items():
        print(f"{resource.title():<12}: {amount:>{width},}")



if __name__ == '__main__':
    reader = easyocr.Reader(['en'])  # English language

    attack_button_template = cv.imread("resources/attack_button.png", cv.IMREAD_GRAYSCALE)
    find_match_button_template = cv.imread("resources/find_match_button.png", cv.IMREAD_GRAYSCALE)
    next_base_button_template = cv.imread("resources/next_base_button.png", cv.IMREAD_GRAYSCALE)
    end_attack_button_template = cv.imread("resources/end_battle_button.png", cv.IMREAD_GRAYSCALE)

    print(utils.get_windows("Clash Of Clans"))
    window = utils.get_windows("Clash Of Clans")[0]
    window.activate()

    utils.search_and_press_template_in_frame(window, utils.get_image(window), attack_button_template)
    time.sleep(1.5)

    utils.search_and_press_template_in_frame(window, utils.get_image(window), find_match_button_template)


    while True:
        image = utils.get_image(window)
        # wait until base loads
        while utils.seach_template_in_frame(utils.get_image(window), end_attack_button_template) is None:
            time.sleep(1.5)

        print(f"waiting for animation to dissapear")
        # make sunt animation disappear
        time.sleep(0.5)

        try:
            print(f"get numbers")
            numbers = extract_resources(image, reader)
        except Exception as e:
            print(e)
            continue

        printResources(numbers)

        if ((numbers["gold"] > 600000 or
             numbers["elixir"] > 600000) and
                numbers["dark elixir"] > 4000):
        # if numbers['dark elixir'] > 10000:
            print("BASE FOUND")
            break
        else:
            print("BASE NOT FOUND")

            try:
                utils.search_and_press_template_in_frame(window, image, next_base_button_template)
                time.sleep(1) # waiting to enter into search mode
            except Exception as e:
                print(e)
                print("when base not found, couldn't press next base button")
                exit(1)