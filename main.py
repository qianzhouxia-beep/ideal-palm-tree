# main.py - Version: v33.2 Stable (Cloud Cluster Final Edition)
import os
import json
import time
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- 核心配置：已指向您的 4GB Zeabur 主战场 ---
NEW_API_BASE = "https://api-tokenmaster.com/v1/chat/completions"
# 已更新为您的 DreamProject 专属 Key
NEW_API_KEY = "sk-NYzKy4W2doTeCxNZX9hIp4SXuxcRYx64AmTbk0i2Qz1twd91" 
DATA_FILE = "/data/referrals.json" 

# 初始化数据文件（确保在紫色硬盘里）
if not os.path.exists("/data"):
    os.makedirs("/data")

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

@app.route('/')
def home():
    return jsonify({
        "status": "Subconscious Mirror Oracle is Live",
        "infra": "Zeabur 4GB Cluster",
        "api_source": "api-tokenmaster.com",
        "project": "DreamProject"
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    messages = data.get('messages', [])
    lang = data.get('lang', 'zh')
    
    system_prompt = {
        "role": "system", 
        "content": (
            "You are a Mysterious Dream Oracle. Analyze dreams with a blend of psychology and mysticism. "
            "Rule 1: Always deliver the report in TWO PARTS (Part A: Deep Analysis, Part B: The Oracle's Prophecy). "
            "Rule 2: At the end of every response, ask exactly ONE follow-up question. "
            f"Rule 3: You MUST respond in {'CHINESE' if lang == 'zh' else 'ENGLISH'}."
        )
    }
    
    try:
        # 调用您的主战场 API
        response = requests.post(
            NEW_API_BASE,
            headers={"Authorization": f"Bearer {NEW_API_KEY}"},
            json={
                "model": "deepseek-r1", # 使用 DeepSeek 顶级模型
                "messages": [system_prompt] + messages, 
                "temperature": 0.7
            },
            timeout=60
        )
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": "Ether Connection Flicker", "details": str(e)}), 500

@app.route('/api/referral', methods=['GET'])
def check_referral():
    inviter_id = request.args.get('id')
    visitor_ip = request.remote_addr
    
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    except:
        data = {}

    if inviter_id:
        if inviter_id not in data:
            data[inviter_id] = {"count": 0, "ips": []}
        if visitor_ip not in data[inviter_id]["ips"]:
            data[inviter_id]["ips"].append(visitor_ip)
            data[inviter_id]["count"] += 1
            with open(DATA_FILE, "w") as f:
                json.dump(data, f)
        return jsonify({"inviter": inviter_id, "count": data[inviter_id]["count"]})
    return jsonify({"status": "active"})

if __name__ == '__main__':
    # 彻底解决 Zeabur 端口解析错误的保护逻辑
    raw_port = os.environ.get("PORT", "5000")
    try:
        target_port = int(raw_port)
    except (ValueError, TypeError):
        target_port = 5000
    
    print(f"Oracle Starting on Port {target_port}...")
    app.run(host='0.0.0.0', port=target_port)
