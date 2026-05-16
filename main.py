# main.py - v33.2.6 (BATTLE-TESTED)
import os
import requests
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS

app = Flask(__name__)
# 允许所有来源、所有方法、所有头
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})

NEW_API_BASE = "https://api-tokenmaster.com/v1/chat/completions"
# 请务必在此处填入您在主战场生成的完整 sk-xxxx 密钥
NEW_API_KEY = "sk-Yb6fOVUVZHJpbMakOSdT8fPF4sUTTS1GwcJeNkGRczdm1EEK" 

def _build_cors_response(data, status=200):
    response = make_response(jsonify(data), status)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

@app.route('/api/referral/init', methods=['GET', 'POST', 'OPTIONS'])
def init_referral():
    return _build_cors_response({"status": "ready", "msg": "Stable Connection!"})

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        return _build_cors_response({})
    
    data = request.json
    try:
        response = requests.post(
            NEW_API_BASE,
            headers={"Authorization": f"Bearer {NEW_API_KEY}"},
            json={
                "model": "deepseek-r1",
                "messages": data.get('messages', []),
                "temperature": 0.7
            },
            timeout=120
        )
        return _build_cors_response(response.json())
    except Exception as e:
        return _build_cors_response({"error": str(e)}, 500)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
