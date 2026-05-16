import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# 核心配置：锁定中转站
API_BASE = "http://43.156.119.47:3000/v1/chat/completions"
API_KEY = "sk-Sef-9i7k]1zjicK6Nv"

@app.route('/')
def home():
    return "Subconscious Mirror Oracle is Live!"

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    messages = data.get('messages', [])
    lang = data.get('lang', 'zh')
    
    # 注入 Oracle 人设
    system_prompt = {
        "role": "system", 
        "content": f"You are a Mysterious Dream Oracle. Analyze dreams in TWO PARTS. Respond in {'CHINESE' if lang == 'zh' else 'ENGLISH'}."
    }
    
    try:
        response = requests.post(
            API_BASE,
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={"model": "deepseek-r1", "messages": [system_prompt] + messages, "temperature": 0.7},
            timeout=60
        )
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": "Ether Flicker", "details": str(e)}), 500

# 核心启动：Zeabur 官方推荐模式
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
