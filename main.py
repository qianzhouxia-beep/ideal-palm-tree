# main.py - Version: v33.2.14 (MASTER FINAL)
import os
import json
import requests
import time
from flask import Flask, request, jsonify, make_response, send_file
from flask_cors import CORS

app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app, supports_credentials=True)

# --- CONFIGURATION ---
NEW_API_BASE = "https://api-tokenmaster.com/v1/chat/completions"
NEW_API_KEY = "sk-biaE1BokgWzky0VkQwX3DuiVCThyVjIlf9BxejJSGi3U0M8j"
HTML_FILE = "dream_pro_landing_v33_referral.html"
DATA_FILE = "referrals.json"
PAYMENTS_FILE = "payments.json"

# Init data
for f_path in [DATA_FILE, PAYMENTS_FILE]:
    if not os.path.exists(f_path):
        with open(f_path, "w") as f: json.dump({}, f)

def load_json(path):
    with open(path, "r") as f: return json.load(f)

def save_json(path, data):
    with open(path, "w") as f: json.dump(data, f)

def _cors(res):
    res.headers["Access-Control-Allow-Origin"] = "*"
    res.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    res.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return res

# --- ROUTES ---

@app.route('/')
def index():
    if os.path.exists(HTML_FILE):
        return send_file(HTML_FILE)
    return "<h1>Mirror Sanctum Error: HTML File Missing</h1>", 404

@app.route('/api/referral/init', methods=['POST', 'OPTIONS'])
def init_ref():
    if request.method == 'OPTIONS': return _cors(make_response())
    # Generate a simple unique ID for referral
    ref_id = f"ref_{int(time.time())}_{os.urandom(2).hex()}"
    data = load_json(DATA_FILE)
    data[ref_id] = {"count": 0, "ips": []}
    save_json(DATA_FILE, data)
    return _cors(jsonify({"status": "ready", "refId": ref_id}))

@app.route('/api/referral/status', methods=['GET'])
def referral_status():
    ref_id = request.args.get('refId')
    data = load_json(DATA_FILE)
    if ref_id in data:
        return _cors(jsonify({"count": data[ref_id]["count"]}))
    return _cors(jsonify({"count": 0}))

@app.route('/api/referral/click', methods=['POST'])
def referral_click():
    inviter_id = request.json.get('refBy')
    visitor_ip = request.remote_addr
    data = load_json(DATA_FILE)
    if inviter_id and inviter_id in data:
        if visitor_ip not in data[inviter_id]["ips"]:
            data[inviter_id]["ips"].append(visitor_ip)
            data[inviter_id]["count"] += 1
            save_json(DATA_FILE, data)
            return _cors(jsonify({"status": "counted", "count": data[inviter_id]["count"]}))
    return _cors(jsonify({"status": "ignored"}))

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS': return _cors(make_response())
    req_data = request.json
    messages = req_data.get('messages', [])
    lang = req_data.get('lang', 'zh')
    
    # Logic: User (1-4) -> Oracle (1-4) -> User (5) -> Report (5)
    user_msg_count = len([m for m in messages if m['role'] == 'user'])
    mode = 'question' if user_msg_count < 5 else 'report'

    system_content = (
        "You are a Mysterious Dream Oracle. Analyze dreams with psychology and mysticism. "
        f"IMPORTANT: You MUST respond in {'CHINESE' if lang == 'zh' else 'ENGLISH'}. "
    )
    if mode == 'question':
        system_content += "Rule: Ask exactly ONE short, provocative follow-up question to dig deeper."
    else:
        part_a = "心理学解析" if lang == 'zh' else "Psychological Analysis"
        part_b = "神谕命运路径" if lang == 'zh' else "The Oracle's Prophecy"
        system_content += (
            f"Rule: Deliver a final report in TWO PARTS. "
            f"PART A: [{part_a}]. PART B: [{part_b}]. "
            "Separate them with the string '---PROPHECY_START---'."
        )

    try:
        response = requests.post(
            NEW_API_BASE,
            headers={"Authorization": f"Bearer {NEW_API_KEY}", "Content-Type": "application/json"},
            json={"model": "deepseek-reasoner", "messages": [{"role": "system", "content": system_content}] + messages, "temperature": 0.8},
            timeout=120
        )
        res_json = response.json()
        ai_msg = res_json['choices'][0]['message']
        text = ai_msg.get('content') or ai_msg.get('reasoning_content') or ""
        
        if mode == 'question':
            return _cors(jsonify({"mode": "question", "content": text}))
        else:
            parts = text.split('---PROPHECY_START---')
            # Handle possible variations in header naming by the AI
            free = parts[0].replace('PART A:', '').replace('[Psychological Analysis]', '').replace('[心理学解析]', '').replace('**[Psychological Analysis]**', '').replace('**[心理学解析]**', '').strip()
            paid = parts[1].replace('PART B:', '').replace("[The Oracle's Prophecy]", '').replace('[神谕命运路径]', '').replace("**[The Oracle's Prophecy]**", '').replace('**[神谕命运路径]**', '').strip() if len(parts) > 1 else "The destiny is veiled..."
            return _cors(jsonify({
                "mode": "report", 
                "content": "The veil is lifted.", 
                "data": {"free_part": free, "paid_part": paid}
            }))
    except Exception as e:
        return _cors(jsonify({"error": str(e)}), 500)

@app.route('/api/gumroad/webhook', methods=['POST'])
def gumroad_webhook():
    gumroad_data = request.form
    email = gumroad_data.get('email')
    if email:
        pay_data = load_json(PAYMENTS_FILE)
        pay_data[email] = {"status": "paid", "timestamp": time.time()}
        save_json(PAYMENTS_FILE, pay_data)
        return "Success", 200
    return "No Email Found", 400

@app.route('/api/check-premium', methods=['GET'])
def check_premium():
    email = request.args.get('email')
    pay_data = load_json(PAYMENTS_FILE)
    if email in pay_data:
        return _cors(jsonify({"status": "unlocked"}))
    return _cors(jsonify({"status": "locked"}))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
