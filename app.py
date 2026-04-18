from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import urllib.request
import urllib.error
import json
import os

app = Flask(__name__, static_folder='.')
CORS(app)

# Render environment variable se API key lega
# Local test ke liye: apni key yahan bhi rakh sakte ho
API_KEY = os.environ.get("OPENROUTER_API_KEY", "YOUR_OPENROUTER_API_KEY")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        messages = data.get('messages', [])

        full_messages = [
            {
                "role": "system",
                "content": "You are PyBot, a friendly and smart AI assistant. Be helpful, clear, and a bit geeky. Use code blocks when sharing code."
            }
        ] + messages

        payload = json.dumps({
            "model": "openrouter/free",
            "messages": full_messages
        }).encode('utf-8')

        req = urllib.request.Request(
            OPENROUTER_URL,
            data=payload,
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + API_KEY,
                'HTTP-Referer': 'https://pybot.onrender.com',
                'X-Title': 'PyBot'
            },
            method='POST'
        )

        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            reply = result['choices'][0]['message']['content']
            model_used = result.get('model', 'unknown')
            print(f"[OK] Model: {model_used}")
            return jsonify({"reply": reply})

    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        return jsonify({"error": "HTTP Error: " + error_body}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("=" * 50)
    print(f"  PyBot Ready! Port: {port}")
    print("=" * 50)
    app.run(host='0.0.0.0', port=port, debug=False)
