import time
import random
import cv2 as cv
import pydirectinput
import pygetwindow
import numpy as np
import base64
import requests
import json
import re
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

def cv_image_to_base64(img):
    # Encode image as PNG in memory
    success, buffer = cv.imencode(".png", img)
    if not success:
        raise ValueError("Could not encode image")

    # Convert to base64 string
    return base64.b64encode(buffer).decode("utf-8")


def parse_number(s: str) -> int:
    cleaned = re.sub(r"[^\d]", "", str(s))
    if not cleaned:
        raise ValueError(f"Invalid number: {s}")
    return int(cleaned)

def extract_resources_from_raw_response(raw_response: str) -> dict:
    # Step 1: extract JSON object (even if model added text around it)
    match = re.search(r"\{.*?\}", raw_response, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON found in response: {raw_response}")

    json_str = match.group(0)

    # Step 2: parse JSON
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON from model: {json_str}") from e

    # Step 3: validate keys
    required_keys = ["gold", "elixir", "dark_elixir"]
    for key in required_keys:
        if key not in data:
            raise ValueError(f"Missing key '{key}' in response: {data}")

    # Step 4: normalize + convert to int
    parsed = {
        "gold": parse_number(data["gold"]),
        "elixir": parse_number(data["elixir"]),
        "dark_elixir": parse_number(data["dark_elixir"]),
    }

    return parsed

def extract_resources(window):
    url = "http://localhost:11434/api/generate"
    image = utils.get_image(window)
    image = image[110:300, 0:240]
    image_base64 = cv_image_to_base64(image)

    prompt = """
You are reading an image that contains exactly 3 resource values, one per line.

Extract the 3 numbers in top-to-bottom order.

Rules:
- Return valid JSON only.
- Do not include markdown.
- Do not include explanations.
- Preserve the digits exactly as seen.
- Keep spaces inside the numbers if they appear in the image.
- Use this exact schema:

{"gold":"...", "elixir":"...", "dark_elixir":"..."}
"""

    payload = {
        "model": "gemma4:e4b",
        "prompt": prompt,
        "images": [image_base64],
        "stream": False
    }

    raw_response = requests.post(url, json=payload).json()["response"]
    print("Raw model response:", raw_response)

    data = extract_resources_from_raw_response(raw_response)
    print("Extracted model response:", data)
    return data

# =========================
# Flow
# =========================

def go_to_search(window, attack_btn, attack_btn2, find_match_btn) -> bool:
    print("Entering search mode…")
    if not click_template(window, attack_btn):
        print("Could not click Attack button.")
        return False

    jitter_sleep(0.8, 1.6)
    if not click_template(window, find_match_btn):
        print("Could not click Find Match button.")
        return False

    jitter_sleep(0.8, 1.6)
    if not click_template(window, attack_btn2):
        print("Could not click Attack2 button.")
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
    attack_button_template = cv.imread("resources/attack_battle_button.png", cv.IMREAD_GRAYSCALE)
    attack2_button_template = cv.imread("resources/attack!_button.png", cv.IMREAD_GRAYSCALE)
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

    if not go_to_search(window, attack_button_template, attack2_button_template, find_match_button_template):
        return

    target = {"gold": 1_000_000, "elixir": 1_000_000, "dark_elixir": 10_000}

    while True:
        if not wait_for_base(window, next_base_button_template, timeout=25.0):
            print("Base did not load in time; retrying Next…")
            if not try_next_base(window, next_base_button_template):
                break
            continue

        print("Reading resources…")
        try:
            resources = extract_resources(window)
        except Exception as e:
            print(f"OCR error: {e}; skipping base.")
            if not try_next_base(window, next_base_button_template):
                break
            continue

        if ((resources["gold"] >= target["gold"]) and
            (resources["elixir"] >= target["elixir"])) and \
                (resources["dark_elixir"] >= target["dark_elixir"]):
            print("BASE FOUND ✅")
            break
        else:
            print("BASE NOT FOUND – skipping.")
            if not try_next_base(window, next_base_button_template):
                print("Couldn’t advance; exiting.")
                break


if __name__ == '__main__':
    main()
