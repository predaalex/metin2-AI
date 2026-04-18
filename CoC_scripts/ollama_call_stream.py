import base64

import requests
import json

def encode_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

url = "http://localhost:11434/api/generate"

image_base64 = encode_image("resources/test.png")

payload = {
    "model": "gemma4:e4b",
    "prompt": "Read the content of the image and just return me exactly the 3 numbers of 3 different lines",
    "images": [image_base64],
    "stream": True
}

with requests.post(url, json=payload, stream=True) as r:
    for line in r.iter_lines():
        if line:
            data = json.loads(line)
            print(data.get("response", ""), end="", flush=True)