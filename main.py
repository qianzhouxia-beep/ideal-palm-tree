# main.py - Version: v34.0.0 (PRO STABLE)
# Optimized by Backend Architect Specialist
import os
import sqlite3
import requests
import time
import uuid
import json
from flask import Flask, request, jsonify, make_response, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# --- SECURITY: Rate Limiting ---
limiter = Limiter(
    get_remote_address,
    app=app,
    storage_uri="memory://",
)

# --- CONFIGURATION (ENV DRIVEN) ---
NEW_API_BASE = os.environ.get("NEW_API_BASE", "https://api-tokenmaster.com/v1/chat/completions")
NEW_API_KEY = os.environ.get("DEEPSEEK_API_KEY") # Required in Env
SM_API_KEY = os.environ.get("SM_API_KEY")       # Required in Env
DB_FILE = "sm_mirror.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """初始化 SQLite 数据库，创建必要的表"""
    conn = get_db_connection()
    cursor = conn.cursor()
    # 推荐人表
    cursor.execute('''CREATE TABLE IF NOT EXISTS referrals (
        ref_id TEXT PRIMARY KEY,
        count INTEGER DEFAULT 0,
        ips TEXT DEFAULT '[]'
    )''')
    # 支付/授权表
    cursor.execute('''CREATE TABLE IF NOT EXISTS payments (
        email TEXT PRIMARY KEY,
        license_key TEXT,
        status TEXT DEFAULT 'unpaid',
        timestamp REAL,
        gumroad_id TEXT
    )''')
    conn.commit()
    conn.close()

# Initialize Database on Startup
init_db()

def _cors(res):
    res.headers["Access-Control-Allow-Origin"] = "*"
    res.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    res.headers["Access-Control-Allow-Headers"] = "Content-Type, X-SM-API-Key"
    return res

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

def require_api_key(f):
    """验证自定义 API Key 的装饰器"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'OPTIONS':
            return _cors(make_response())
        provided_key = request.headers.get("X-SM-API-Key")
        if not SM_API_KEY or provided_key != SM_API_KEY:
            return _cors(jsonify({"error": "Unauthorized Access"})), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
@require_api_key
@limiter.limit("5 per minute")
def chat():
    if request.method == 'OPTIONS': return _cors(make_response())
    req_data = request.json
    messages = req_data.get('messages', [])
    lang = req_data.get('lang', 'zh')
    user_email = req_data.get('email')
    
    # Verify Premium Status via Database
    is_premium = False
    if user_email:
        conn = get_db_connection()
        row = conn.execute('SELECT status FROM payments WHERE email = ?', (user_email,)).fetchone()
        conn.close()
        if row and row['status'] == 'paid':
            is_premium = True
    
    # Logic: Oracle Behavior
    user_msg_count = len([m for m in messages if m['role'] == 'user'])
    mode = 'question' if user_msg_count < 5 else 'report'

    lang_instruction = "CHINESE (Simplified)" if lang == 'zh' else "ENGLISH"
    warning_msg = "再这样我就生气了😡！" if lang == 'zh' else "Don't make me angry! 😡"
    
    system_content = (
        "You are a Mysterious Dream Oracle. Analyze dreams with psychology and mysticism. "
        "Maintain a vibe of ancient mystery but be 'smart' and witty. "
        f"CRITICAL: You MUST respond EXCLUSIVELY in {lang_instruction}. "
        "If the user provides very short, lazy, or nonsensical input (like just a single number, letter, or emoji), "
        "do not be overly solemn. Respond with wit, gentle irony, or humor while staying in character as a cryptic sage. "
        "Acknowledge their 'minimalist' approach (e.g., 'A dream as brief as a single breath...', 'You are being stingy with your subconscious treasures...') "
        "before asking a provocative follow-up. "
        f"If they are being persistent with nonsense or laziness, you can end with a humorous warning like '{warning_msg}'."
    )

    if mode == 'question':
        system_content += " Rule: Ask exactly ONE short, provocative follow-up question."
    else:
        part_a = "心理学解析" if lang == 'zh' else "Psychological Analysis"
        part_b = "神谕命运路径" if lang == 'zh' else "The Oracle's Prophecy"
        system_content += (
            f" Rule: Deliver a report in TWO PARTS: PART A: [{part_a}] and PART B: [{part_b}]. "
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
            free = parts[0].strip()
            paid = parts[1].strip() if len(parts) > 1 else "The destiny remains veiled..."
            return _cors(jsonify({
                "mode": "report", 
                "status": "full" if is_premium else "partial",
                "data": {"free_part": free, "paid_part": paid}
            }))
    except Exception as e:
        return _cors(jsonify({"error": str(e)}), 500)

@app.route('/api/verify-license', methods=['POST', 'OPTIONS'])
@require_api_key
def verify_license():
    if request.method == 'OPTIONS': return _cors(make_response())
    data = request.json
    license_key = data.get('license_key')
    product_permalink = "subconscious-mirror" 
    
    try:
        res = requests.post(
            "https://api.gumroad.com/v2/licenses/verify",
            data={"product_permalink": product_permalink, "license_key": license_key},
            timeout=10
        )
        res_data = res.json()
        if res_data.get('success') is True:
            purchase_data = res_data.get('purchase', {})
            email = purchase_data.get('email')
            conn = get_db_connection()
            conn.execute('INSERT OR REPLACE INTO payments (email, license_key, status, timestamp, gumroad_id) VALUES (?, ?, ?, ?, ?)',
                        (email, license_key, 'paid', time.time(), purchase_data.get('gumroad_id')))
            conn.commit()
            conn.close()
            return _cors(jsonify({"status": "unlocked", "email": email}))
        return _cors(jsonify({"status": "failed", "message": "Invalid license key"})), 400
    except Exception as e:
        return _cors(jsonify({"error": str(e)}), 500)

@app.route('/api/referral/init', methods=['POST', 'OPTIONS'])
@require_api_key
def init_referral():
    if request.method == 'OPTIONS': return _cors(make_response())
    ref_id = f"ref_{int(time.time())}_{uuid.uuid4().hex[:4]}"
    conn = get_db_connection()
    conn.execute('INSERT INTO referrals (ref_id, count, ips) VALUES (?, 0, ?)', (ref_id, '[]'))
    conn.commit()
    conn.close()
    return _cors(jsonify({"refId": ref_id}))

@app.route('/api/referral/click', methods=['POST', 'OPTIONS'])
@require_api_key
def referral_click():
    if request.method == 'OPTIONS': return _cors(make_response())
    data = request.json
    ref_by = data.get('refBy')
    ip = get_remote_address()
    if not ref_by: return _cors(jsonify({"error": "No ref code"})), 400
    
    conn = get_db_connection()
    row = conn.execute('SELECT count, ips FROM referrals WHERE ref_id = ?', (ref_by,)).fetchone()
    if row:
        ips = json.loads(row['ips'])
        if ip not in ips:
            ips.append(ip)
            conn.execute('UPDATE referrals SET count = count + 1, ips = ? WHERE ref_id = ?', (json.dumps(ips), ref_by))
            conn.commit()
    conn.close()
    return _cors(jsonify({"status": "ok"}))

@app.route('/api/referral/status', methods=['GET', 'OPTIONS'])
@require_api_key
def referral_status():
    if request.method == 'OPTIONS': return _cors(make_response())
    ref_id = request.args.get('refId')
    conn = get_db_connection()
    row = conn.execute('SELECT count FROM referrals WHERE ref_id = ?', (ref_id,)).fetchone()
    conn.close()
    return _cors(jsonify({"count": row['count'] if row else 0}))

@app.route('/api/check-premium', methods=['GET', 'OPTIONS'])
@require_api_key
def check_premium():
    if request.method == 'OPTIONS': return _cors(make_response())
    email = request.args.get('email')
    if not email: return _cors(jsonify({"premium": False}))
    conn = get_db_connection()
    row = conn.execute('SELECT status FROM payments WHERE email = ?', (email,)).fetchone()
    conn.close()
    return _cors(jsonify({"premium": row and row['status'] == 'paid'}))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port)
