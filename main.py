# main.py - Version: v33.2.9 (PRODUCTION REASONER EDITION)
import os
import requests
from flask import Flask, request, jsonify, make_response, send_file
from flask_cors import CORS

app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})

# --- 核心配置区 ---
NEW_API_BASE = "https://api-tokenmaster.com/v1/chat/completions"
# 请确保使用完整的 sk-xxxx 密钥
NEW_API_KEY = "sk-biaE1BokgWzky0VkQwX3DuiVCThyVjIlf9BxejJSGi3U0M8j" 
HTML_FILE = "dream_pro_landing_v33_referral.html"

def _build_cors_response(data, status=200):
    response = make_response(jsonify(data), status)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

@app.route('/')
def serve_index():
    if os.path.exists(HTML_FILE):
        return send_file(HTML_FILE)
    return "<h1>Error: HTML File Missing</h1>", 404

@app.route('/api/referral/init', methods=['GET', 'POST', 'OPTIONS'])
def init_referral():
    return _build_cors_response({"status": "ready", "version": "v33.2.9"})

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        return _build_cors_response({})
    
    data = request.json
    messages = data.get('messages', [])
    lang = data.get('lang', 'zh')
    
    system_prompt = {
        "role": "system",
        "content": (
            "You are a Mysterious Dream Oracle. Analyze dreams with psychology and mysticism. "
            "Rule 1: Deliver report in TWO PARTS (Part A: Analysis, Part B: Prophecy). "
            "Rule 2: Ask ONE follow-up question. "
            f"Rule 3: You MUST respond in {'Chinese' if lang == 'zh' else 'English'}."
        )
    }
    
    try:
        response = requests.post(
            NEW_API_BASE,
            headers={"Authorization": f"Bearer {NEW_API_KEY}"},
            json={
                "model": "deepseek-reasoner", # 改回这个已经定价的名字！
                "messages": [system_prompt] + messages,
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
