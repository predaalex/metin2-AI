import time

import cv2 as cv
import pydirectinput
import pygetwindow
import easyocr

import opencv_utils as utils
import re


def extract_text_from_image(image):
    cropped = image[135:270, 0:250]
    padded = cv.copyMakeBorder(
        cropped,
        top=10, bottom=10,
        left=20, right=20,
        borderType=cv.BORDER_CONSTANT,
        value=[0, 0, 0]  # white padding
    )

    cv.imshow("cropped", padded)
    cv.waitKey(1)

    # Run OCR
    results = reader.readtext(padded, detail=1)

    # Group results by line using Y-coordinate of bounding boxes
    lines = []
    line_threshold = 15  # max vertical difference to group into the same line

    for (bbox, text, conf) in results:
        y_center = (bbox[0][1] + bbox[2][1]) / 2

        # Try to place the text into an existing line
        placed = False
        for line in lines:
            if abs(line['y'] - y_center) < line_threshold:
                line['words'].append((bbox[0][0], text))  # (x position, text)
                placed = True
                break

        # If not placed, start a new line
        if not placed:
            lines.append({'y': y_center, 'words': [(bbox[0][0], text)]})

    # Sort each line's words by horizontal position
    for line in lines:
        line['words'].sort(key=lambda x: x[0])

    # Final line-by-line output
    line_texts = [" ".join(word for _, word in line['words']) for line in lines]
    line_texts = [int(line.replace(" ", "")) for line in line_texts]
    # Print or return results
    for i, line in enumerate(line_texts):
        print(f"Line {i + 1}: {line}")

    return line_texts


def extract_resources(image):
    text = extract_text_from_image(image)

    resources = {
        "gold": text[0],
        "elixir": text[1],
        "dark elixir": text[2]
    }

    return resources


if __name__ == '__main__':
    reader = easyocr.Reader(['en'])  # English language

    attack_button_template = cv.imread("resources/attack_button.png", cv.IMREAD_GRAYSCALE)
    find_match_button_template = cv.imread("resources/find_match_button.png", cv.IMREAD_GRAYSCALE)
    next_base_button_template = cv.imread("resources/next_base_button.png", cv.IMREAD_GRAYSCALE)
    test_img = cv.imread("resources/test_img.png", cv.IMREAD_GRAYSCALE)

    print(utils.get_windows("Clash Of Clans"))
    window = utils.get_windows("Clash Of Clans")[0]
    window.activate()

    utils.search_and_press_template_in_frame(window, utils.get_image(window), attack_button_template)
    time.sleep(1)

    utils.search_and_press_template_in_frame(window, utils.get_image(window), find_match_button_template)
    time.sleep(10)

    while True:
        image = utils.get_image(window)

        try:
            numbers = extract_resources(image)
        except Exception as e:
            print(e)
            continue
        print(numbers)

        if ((numbers["gold"] > 900000 or
            numbers["elixir"] > 900000) and
            numbers["dark elixir"] > 6000):
            print("BASE FOUND")
            break

        utils.search_and_press_template_in_frame(window, image, next_base_button_template)
        time.sleep(10)

