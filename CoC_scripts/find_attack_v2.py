import time
import random
import cv2 as cv
import easyocr
import pydirectinput
import pygetwindow
import numpy as np

import opencv_utils as utils  # your helper module


# =========================
# Utility helpers
# =========================

def jitter_sleep(a: float, b: float) -> None:
    """Sleep random time in [a,b] seconds."""
    time.sleep(random.uniform(a, b))


def mean_abs_diff(a: np.ndarray, b: np.ndarray) -> float:
    if a.ndim == 3:
        a = cv.cvtColor(a, cv.COLOR_BGR2GRAY)
    if b.ndim == 3:
        b = cv.cvtColor(b, cv.COLOR_BGR2GRAY)
    return float(np.mean(cv.absdiff(a, b)))


def wait_for_stable_view(get_frame_fn,
                         region=None,
                         settle_threshold: float = 1.0,
                         consecutive: int = 3,
                         timeout: float = 5.0,
                         interval: float = 0.2) -> bool:
    """Wait until frames stop changing much."""
    t0 = time.time()
    last = None
    stable_count = 0

    while time.time() - t0 < timeout:
        frame = get_frame_fn()
        if region:
            y1, x1, y2, x2 = region
            frame = frame[y1:y2, x1:x2]
        if last is not None:
            mad = mean_abs_diff(last, frame)
            if mad <= settle_threshold:
                stable_count += 1
                if stable_count >= consecutive:
                    return True
            else:
                stable_count = 0
        last = frame
        time.sleep(interval)
    return False


def wait_for_template(window,
                      template: np.ndarray,
                      threshold: float = 0.82,
                      must_hold_ms: int = 250,
                      timeout: float = 15.0,
                      check_interval: float = 0.15) -> bool:
    """Wait until a template appears and stays for a bit."""
    t0 = time.time()
    first_hit = None
    while time.time() - t0 < timeout:
        frame = utils.get_image(window)
        pt = utils.seach_template_in_frame(frame, template)
        if pt is not None:
            if first_hit is None:
                first_hit = time.time()
            elif (time.time() - first_hit) * 1000 >= must_hold_ms:
                return True
        else:
            first_hit = None
        time.sleep(check_interval)
    return False


def click_template(window,
                   template: np.ndarray,
                   threshold: float = 0.85,
                   retries: int = 3) -> bool:
    """Click a template in the current frame."""
    for _ in range(retries):
        frame = utils.get_image(window)
        try:
            utils.search_and_press_template_in_frame(window, frame, template)
            return True
        except Exception:
            jitter_sleep(0.10, 0.25)
    return False


# =========================
# OCR (your original method)
# =========================

def extract_text_from_image(image,
                          crop_rect=(135, 0, 270, 250),
                          scale=4,
                          reader=None):
    """
    Crop the 3-line panel and OCR each band into ints.
    Returns list of three ints [gold, elixir, dark elixir].
    """
    y1, x1, y2, x2 = crop_rect
    roi = image[y1:y2, x1:x2]

    # upscale
    image = cv.resize(roi, None, fx=scale, fy=scale, interpolation=cv.INTER_CUBIC)

    # denoise
    image = cv.GaussianBlur(image, (5,5), 0)

    # threshold + invert
    _, bw = cv.threshold(image, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)

    # morph open
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (3,3))
    clean = cv.morphologyEx(bw, cv.MORPH_OPEN, kernel, iterations=1)
    clean = cv.bitwise_not(clean)

    # split into bands
    h = clean.shape[0]
    bands = [ clean[int(i*h/3):int((i+1)*h/3), :] for i in range(3) ]

    nums = []
    for band in bands:
        txts = reader.readtext(band,
                               detail=0,
                               text_threshold=0.3,
                               allowlist='0123456789')
        joined = ''.join(txts)
        digit_str = ''.join([c for c in joined if c.isdigit()])
        if digit_str == "":
            raise ValueError("OCR failed to read digits")
        nums.append(int(digit_str))

    return nums


def extract_resources(image, reader):
    gold, elix, dark = extract_text_from_image(image, reader=reader)
    return {"gold": gold, "elixir": elix, "dark elixir": dark}


def print_resources(numbers):
    width = len(f"{max(numbers.values()):,}")
    for resource, amount in numbers.items():
        print(f"{resource.title():<12}: {amount:>{width},}")


# =========================
# Flow
# =========================

def go_to_search(window, attack_btn, find_match_btn) -> bool:
    print("Entering search mode…")
    if not click_template(window, attack_btn):
        print("Could not click Attack button.")
        return False
    jitter_sleep(0.8, 1.6)
    if not click_template(window, find_match_btn):
        print("Could not click Find Match button.")
        return False
    return True


def wait_for_base(window,
                  next_base_btn,
                  timeout: float = 20.0) -> bool:
    print("Waiting for base to load…")
    ok = wait_for_template(window, next_base_btn, threshold=0.83, timeout=timeout)
    if not ok:
        print("Timeout waiting for base HUD.")
        return False
    wait_for_stable_view(lambda: utils.get_image(window),
                         region=(120, 0, 290, 300),
                         settle_threshold=1.2,
                         consecutive=3,
                         timeout=5.0,
                         interval=0.2)
    return True


def try_next_base(window, next_btn) -> bool:
    print("Skipping to next base…")
    ok = click_template(window, next_btn)
    if not ok:
        print("Could not click Next Base button.")
    else:
        jitter_sleep(0.7, 1.2)
    return ok


# =========================
# Main
# =========================

def main():
    # Init OCR
    reader = easyocr.Reader(['en'], gpu=True)

    attack_button_template = cv.imread("resources/attack_button.png", cv.IMREAD_GRAYSCALE)
    find_match_button_template = cv.imread("resources/find_match_button.png", cv.IMREAD_GRAYSCALE)
    next_base_button_template = cv.imread("resources/next_base_button.png", cv.IMREAD_GRAYSCALE)
    end_attack_button_template = cv.imread("resources/end_battle_button.png", cv.IMREAD_GRAYSCALE)

    wins = utils.get_windows("Clash Of Clans")
    if not wins:
        print("Clash Of Clans window not found.")
        return
    window = wins[0]
    window.activate()
    jitter_sleep(0.3, 0.6)

    if not go_to_search(window, attack_button_template, find_match_button_template):
        return

    target = {"gold": 500_000, "elixir": 900_000, "dark elixir": 1_000}

    while True:
        if not wait_for_base(window, next_base_button_template, timeout=25.0):
            print("Base did not load in time; retrying Next…")
            if not try_next_base(window, next_base_button_template):
                break
            continue

        print("Reading resources…")
        try:
            image = utils.get_image(window)
            resources = extract_resources(image, reader)
        except Exception as e:
            print(f"OCR error: {e}; skipping base.")
            if not try_next_base(window, next_base_button_template):
                break
            continue

        print_resources(resources)

        if ((resources["gold"] >= target["gold"]) and
            (resources["elixir"] >= target["elixir"])) and \
                (resources["dark elixir"] >= target["dark elixir"]):
            print("BASE FOUND ✅")
            break
        else:
            print("BASE NOT FOUND – skipping.")
            if not try_next_base(window, next_base_button_template):
                print("Couldn’t advance; exiting.")
                break


if __name__ == '__main__':
    main()
