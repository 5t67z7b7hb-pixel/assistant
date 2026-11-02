import requests
import json

def stream_ollama_response(user_input):
    url = "http://localhost:11434/api/chat"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": "llama3",
        "stream": True,
        "messages": [
            {"role": "user", "content": user_input}
        ]
    }

    print("\n🤖 AI-generated Answer (streaming):")

    with requests.post(url, headers=headers, json=payload, stream=True) as response:
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                if 'message' in data and 'content' in data['message']:
                    print(data['message']['content'], end='', flush=True)
