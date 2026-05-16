# main.py - Version: v33.2.5 (THE UNSTOPPABLE VERSION)
import os
import requests
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS

app = Flask(__name__)
# 禁用严格斜杠检查，解决 405 和路径匹配问题
app.url_map.strict_slashes = False
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})

# 配置主战场
NEW_API_BASE = "https://api-tokenmaster.com/v1/chat/completions"
# 请务必在此处填入您在主战场生成的完整 sk-xxxx 密钥
NEW_API_KEY = "sk-Yb6fOVUVZHJpbMakOSdT8fPF4sUTTS1GwcJeNkGRczdm1EEK" 

def _add_cors_headers(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response

@app.route('/')
def index():
    return "<h1>Dream Mirror Backend is Running!</h1>"

# 核心初始化接口：允许 GET 和 POST
@app.route('/api/referral/init', methods=['GET', 'POST', 'OPTIONS'])
def init_referral():
    if request.method == 'OPTIONS':
        return _add_cors_headers(make_response())
    res = jsonify({"status": "ready", "msg": "Mirror connected successfully!"})
    return _add_cors_headers(res)

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        return _add_cors_headers(make_response())
        
    data = request.json
    messages = data.get('messages', [])
    lang = data.get('lang', 'zh')
    
    try:
        response = requests.post(
            NEW_API_BASE,
            headers={
                "Authorization": f"Bearer {NEW_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-r1", # 已经过主战场映射
                "messages": [
                    {"role": "system", "content": f"You are a Mysterious Dream Oracle. Output in {'Chinese' if lang=='zh' else 'English'}."}
                ] + messages
            },
            timeout=120
        )
        return _add_cors_headers(jsonify(response.json()))
    except Exception as e:
        return _add_cors_headers(jsonify({"error": str(e)})), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
