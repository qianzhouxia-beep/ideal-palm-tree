from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import os
import time

app = Flask(__name__)
CORS(app)

# --- 配置 ---
NEW_API_BASE = "http://43.156.119.47:3000/v1/chat/completions"
NEW_API_KEY = "sk-Sef-9i7k]1zjicK6Nv"
DATA_FILE = "referrals.json"
PAYMENTS_FILE = "payments.json"

# 初始化数据文件
for f_path in [DATA_FILE, PAYMENTS_FILE]:
    if not os.path.exists(f_path):
        with open(f_path, "w") as f:
            json.dump({}, f)

# --- 核心逻辑 (Referral + Gumroad) ---
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    messages = data.get('messages', [])
    lang = data.get('lang', 'zh')
    system_prompt = {
        "role": "system", 
        "content": f"You are a Mysterious Dream Oracle. Analyze dreams in TWO PARTS (Deep Analysis & Prophecy). Respond in {'CHINESE' if lang == 'zh' else 'ENGLISH'}."
    }
    try:
        response = requests.post(NEW_API_BASE, headers={"Authorization": f"Bearer {NEW_API_KEY}"},
                                 json={"model": "deepseek-r1", "messages": [system_prompt] + messages, "temperature": 0.7}, timeout=60)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": "Ether Flicker", "details": str(e)}), 500

@app.route('/api/referral', methods=['GET'])
def referral():
    return jsonify({"status": "active", "msg": "Hermes Oracle Live"})

# --- 启动配置 (Zeabur 专用) ---
if __name__ == '__main__':
    # 获取 Zeabur 自动分配的端口，如果没有则默认 5000
    port = int(os.environ.get("PORT", 5000))
    # host 必须是 0.0.0.0 才能接收公网访问
    app.run(host='0.0.0.0', port=port)
