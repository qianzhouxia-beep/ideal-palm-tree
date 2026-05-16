# main.py - Version: v33.2.2 Stable (REED MASTER EDITION)
import os
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# 彻底放开跨域，确保本地测试 100% 成功
CORS(app, resources={r"/api/*": {"origins": "*"}})

# --- 核心配置：已指向您的 4GB Zeabur 主战场 ---
NEW_API_BASE = "https://api-tokenmaster.com/v1/chat/completions"
# 已更新为您的最新 dream_api 令牌
NEW_API_KEY = "sk-Yb6fOVUVZHJpbMakOSdT8fPF4sUTTS1GwcJeNkGRczdm1EEK" 
DATA_FILE = "/data/referrals.json"

@app.route('/')
def home():
    return jsonify({
        "status": "Subconscious Mirror Oracle is Live",
        "infra": "Zeabur 4GB Cluster",
        "project": "DreamProject",
        "model": "DeepSeek-R1"
    })

@app.route('/api/referral/init', methods=['GET', 'OPTIONS'])
def init_referral():
    return jsonify({"status": "initialized", "message": "Oracle is ready"})

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        return '', 200
        
    data = request.json
    messages = data.get('messages', [])
    lang = data.get('lang', 'zh')
    
    # 神秘学先知提示词（黄金标准）
    system_prompt = {
        "role": "system", 
        "content": (
            "You are a Mysterious Dream Oracle. Analyze dreams with psychology and mysticism. "
            "Rule 1: Deliver report in TWO PARTS (Part A: Deep Analysis, Part B: The Oracle's Prophecy). "
            "Rule 2: At the end of every response, ask exactly ONE follow-up question. "
            f"Rule 3: You MUST respond in {'CHINESE' if lang == 'zh' else 'ENGLISH'}."
        )
    }
    
    try:
        # 发送请求到您的主战场
        response = requests.post(
            NEW_API_BASE,
            headers={"Authorization": f"Bearer {NEW_API_KEY}"},
            json={
                "model": "deepseek-chat", # 兼容性最好的模型名
                "messages": [system_prompt] + messages, 
                "temperature": 0.7
            },
            timeout=60
        )
        return jsonify(response.json())
    except Exception as e:
        # 统一错误响应，避免前端解析失败
        return jsonify({"error": "Ether Connection Flicker", "details": str(e)}), 500

@app.route('/api/referral', methods=['GET'])
def check_referral():
    inviter_id = request.args.get('id')
    return jsonify({"status": "active", "inviter": inviter_id})

if __name__ == '__main__':
    # 强制处理 Zeabur 端口解析
    port = int(os.environ.get("PORT", 5000))
    print(f"Oracle Starting on Port {port}...")
    app.run(host='0.0.0.0', port=port)
