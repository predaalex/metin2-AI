import requests

url = "http://localhost:11434/api/generate"

payload = {
    "model": "gemma4:e4b",
    "prompt": "Explain recursion in simple terms.",
    "stream": False
}

response = requests.post(url, json=payload)

print(response.json()["response"])