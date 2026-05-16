# main.py - Version: v33.2 Stable (FIXED PORT BUG)
import os
import json
import time
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- CONFIGURATION ---
NEW_API_BASE = "http://43.156.119.47:3000/v1/chat/completions"
NEW_API_KEY = "sk-Sef-9i7k]1zjicK6Nv" 
DATA_FILE = "referrals.json"
PAYMENTS_FILE = "payments.json"

# Initialize data files
for f_path in [DATA_FILE, PAYMENTS_FILE]:
    if not os.path.exists(f_path):
        with open(f_path, "w") as f:
            json.dump({}, f)

def get_json_data(path):
    with open(path, "r") as f:
        return json.load(f)

def save_json_data(path, data):
    with open(path, "w") as f:
        json.dump(data, f)

# --- ENDPOINTS ---
@app.route('/')
def home():
    return jsonify({"status": "Subconscious Mirror Oracle is Live", "version": "v33.2"})

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
        response = requests.post(
            NEW_API_BASE,
            headers={"Authorization": f"Bearer {NEW_API_KEY}"},
            json={"model": "deepseek-r1", "messages": [system_prompt] + messages, "temperature": 0.7},
            timeout=60
        )
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": "Ether Connection Flicker", "details": str(e)}), 500

@app.route('/api/referral', methods=['GET'])
def check_referral():
    inviter_id = request.args.get('id')
    visitor_ip = request.remote_addr
    data = get_json_data(DATA_FILE)
    if inviter_id:
        if inviter_id not in data:
            data[inviter_id] = {"count": 0, "ips": []}
        if visitor_ip not in data[inviter_id]["ips"]:
            data[inviter_id]["ips"].append(visitor_ip)
            data[inviter_id]["count"] += 1
            save_json_data(DATA_FILE, data)
        return jsonify({"inviter": inviter_id, "count": data[inviter_id]["count"]})
    return jsonify({"status": "active"})

@app.route('/api/gumroad/webhook', methods=['POST'])
def gumroad_webhook():
    gumroad_data = request.form
    email = gumroad_data.get('email')
    if email:
        pay_data = get_json_data(PAYMENTS_FILE)
        pay_data[email] = {"status": "paid", "product": gumroad_data.get('product_name'), "timestamp": time.time()}
        save_json_data(PAYMENTS_FILE, pay_data)
        return "Success", 200
    return "No Email Found", 400

@app.route('/api/check-premium', methods=['GET'])
def check_premium():
    email = request.args.get('email')
    pay_data = get_json_data(PAYMENTS_FILE)
    if email in pay_data:
        return jsonify({"status": "unlocked", "product": pay_data[email]["product"]})
    return jsonify({"status": "locked"})

if __name__ == '__main__':
    # --- CRITICAL FIX: Robust Port Handling ---
    raw_port = os.environ.get("PORT", "5000")
    try:
        # If Zeabur gives "${WEB_PORT}" string, this will fail and fallback to 5000
        target_port = int(raw_port)
    except (ValueError, TypeError):
        target_port = 5000
    
    print(f"Starting Oracle on port {target_port}...")
    app.run(host='0.0.0.0', port=target_port)
