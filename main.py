# main.py - Version: v34.0.0 (PRO STABLE)
# Optimized by Backend Architect Specialist
import os
import sqlite3
import requests
import time
import uuid
from flask import Flask, request, jsonify, make_response, send_file
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps

app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app, supports_credentials=True)

# --- RATE LIMITING ---
limiter = Limiter(
    get_remote_address,
    app=app,
    storage_uri="memory://",
)

# --- CONFIGURATION (ENV DRIVEN) ---
# 建议在服务器设置环境变量，若本地测试可在此填入默认值
NEW_API_BASE = os.environ.get("NEW_API_BASE", "https://api-tokenmaster.com/v1/chat/completions")
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
SM_API_KEY = os.environ.get("SM_API_KEY", "sm-mirror-secret")
HTML_FILE = "dream_pro_landing_v33_referral.html"
DB_FILE = "sm_mirror.db"

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'OPTIONS':
            return f(*args, **kwargs)
        api_key = request.headers.get('X-SM-API-Key')
        if api_key != SM_API_KEY:
            return _cors(jsonify({"error": "Unauthorized"}), 401)
        return f(*args, **kwargs)
    return decorated_function

# --- DATABASE LAYER ---
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
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    # 推荐点击日志 (防作弊)
    cursor.execute('''CREATE TABLE IF NOT EXISTS referral_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ref_id TEXT,
                        visitor_ip TEXT,
                        user_agent TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(ref_id, visitor_ip, user_agent))''')
    # 支付记录表
    cursor.execute('''CREATE TABLE IF NOT EXISTS payments (
                        email TEXT PRIMARY KEY,
                        status TEXT,
                        license_key TEXT,
                        timestamp REAL)''')
    conn.commit()
    conn.close()

# 执行初始化
init_db()

@app.errorhandler(Exception)
def handle_exception(e):
    return _cors(jsonify({"error": "Internal Server Error", "details": str(e)}), 500)

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
@require_api_key
def init_ref():
    if request.method == 'OPTIONS': return _cors(make_response())
    ref_id = f"ref_{int(time.time())}_{os.urandom(2).hex()}"
    conn = get_db_connection()
    conn.execute("INSERT INTO referrals (ref_id, count) VALUES (?, ?)", (ref_id, 0))
    conn.commit()
    conn.close()
    return _cors(jsonify({"status": "ready", "refId": ref_id}))

@app.route('/api/referral/status', methods=['GET'])
@require_api_key
def referral_status():
    ref_id = request.args.get('refId')
    conn = get_db_connection()
    row = conn.execute("SELECT count FROM referrals WHERE ref_id = ?", (ref_id,)).fetchone()
    conn.close()
    return _cors(jsonify({"count": row["count"] if row else 0}))

@app.route('/api/referral/click', methods=['POST'])
@require_api_key
def referral_click():
    inviter_id = request.json.get('refBy')
    visitor_ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', 'unknown')
    
    if not inviter_id:
        return _cors(jsonify({"status": "ignored"}))

    conn = get_db_connection()
    try:
        # 插入日志，如果触发 UNIQUE 约束说明是重复点击
        conn.execute("INSERT INTO referral_logs (ref_id, visitor_ip, user_agent) VALUES (?, ?, ?)", 
                     (inviter_id, visitor_ip, user_agent))
        # 更新计数
        conn.execute("UPDATE referrals SET count = count + 1 WHERE ref_id = ?", (inviter_id,))
        conn.commit()
        
        row = conn.execute("SELECT count FROM referrals WHERE ref_id = ?", (inviter_id,)).fetchone()
        return _cors(jsonify({"status": "counted", "count": row["count"] if row else 0}))
    except sqlite3.IntegrityError:
        # 已存在的点击记录
        return _cors(jsonify({"status": "ignored"}))
    finally:
        conn.close()

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
@limiter.limit("5 per minute")
@require_api_key
def chat():
    if request.method == 'OPTIONS': return _cors(make_response())
    req_data = request.json
    messages = req_data.get('messages', [])
    lang = req_data.get('lang', 'zh')
    user_email = req_data.get('email')

    # Character limit check
    for msg in messages:
        if len(msg.get('content', '')) > 5000:
            return _cors(jsonify({"error": "Message too long (max 5000 chars)"}), 400)
    
    # Verify Premium Status via SQLite
    is_premium = False
    if user_email:
        conn = get_db_connection()
        row = conn.execute("SELECT status FROM payments WHERE email = ?", (user_email,)).fetchone()
        conn.close()
        if row and row['status'] == 'paid':
            is_premium = True
    
    user_msg_count = len([m for m in messages if m['role'] == 'user'])
    mode = 'question' if user_msg_count < 5 else 'report'

    warning_msg = "再这样我就生气了😡！" if lang == 'zh' else "Don't make me angry! 😡"
    system_content = (
        "You are a Mysterious Dream Oracle. Analyze dreams with psychology and mysticism. "
        "Maintain a vibe of ancient mystery but be 'smart' and witty. "
        "IMPORTANT: You MUST respond in {'CHINESE' if lang == 'zh' else 'ENGLISH'}. "
    )
    if mode == 'question':
        system_content += "Rule: Ask exactly ONE short, provocative follow-up question to dig deeper."
    else:
        system_content += "Rule: Deliver a final report in TWO PARTS. Separate with '---PROPHECY_START---'."

    try:
        response = requests.post(
            NEW_API_BASE,
            headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"},
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
            paid = parts[1].strip() if len(parts) > 1 else "The destiny is veiled..."
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
            email = res_data['purchase']['email']
            conn = get_db_connection()
            conn.execute("INSERT OR REPLACE INTO payments (email, status, license_key, timestamp) VALUES (?, ?, ?, ?)",
                         (email, 'paid', license_key, time.time()))
            conn.commit()
            conn.close()
            return _cors(jsonify({"status": "unlocked", "email": email}))
        return _cors(jsonify({"status": "failed", "message": "Invalid license key"}), 400)
    except Exception as e:
        return _cors(jsonify({"error": str(e)}), 500)

@app.route('/api/check-premium', methods=['GET'])
@require_api_key
def check_premium():
    email = request.args.get('email')
    conn = get_db_connection()
    row = conn.execute("SELECT status FROM payments WHERE email = ?", (email,)).fetchone()
    conn.close()
    if row and row['status'] == 'paid':
        return _cors(jsonify({"status": "unlocked"}))
    return _cors(jsonify({"status": "locked"}))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
