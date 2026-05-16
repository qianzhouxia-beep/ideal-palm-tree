# main.py - Version: v33.2.12 (THE FINAL MIRROR FIX)
import os
import requests
from flask import Flask, request, jsonify, make_response, send_file
from flask_cors import CORS

app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})

# --- 核心配置区 ---
NEW_API_BASE = "https://api-tokenmaster.com/v1/chat/completions"
# 确认这是您在游乐场测试通过的最新 Mirror API 密钥
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
    return f"<h1>Oracle Error</h1><p>File {HTML_FILE} missing.</p>", 404

@app.route('/api/referral/init', methods=['GET', 'POST', 'OPTIONS'])
def init_referral():
    return _build_cors_response({"status": "ready", "version": "v33.2.12"})

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
            "Analyze dreams with psychology and mysticism. "
            "Deliver report in TWO PARTS (Part A: Analysis, Part B: Prophecy). "
            "Ask ONE follow-up question. "
            f"Respond in {'Chinese' if lang == 'zh' else 'English'}."
        )
    }
    
    try:
        response = requests.post(
            NEW_API_BASE,
            headers={"Authorization": f"Bearer {NEW_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "deepseek-reasoner",
                "messages": [system_prompt] + messages,
                "temperature": 0.7
            },
            timeout=120
        )
        
        # --- 核心修复逻辑 ---
        res_json = response.json()
        
        if "choices" in res_json and len(res_json["choices"]) > 0:
            msg = res_json["choices"][0]["message"]
            
            # 提取内容：优先取 content，如果为空则取 reasoning_content
            final_text = msg.get("content") or msg.get("reasoning_content") or "The Oracle is silent..."
            
            # 强制重构为前端网页 100% 认识的格式
            res_json["choices"][0]["message"]["content"] = final_text
            
        return _build_cors_response(res_json)

    except Exception as e:
        return _build_cors_response({"error": str(e)}, 500)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
