# main.py - Version: v33.2.8 (UNIFIED PRODUCTION STABLE)
import os
import requests
from flask import Flask, request, jsonify, make_response, send_file
from flask_cors import CORS

app = Flask(__name__)
# 禁用严格斜杠检查，增强路径兼容性
app.url_map.strict_slashes = False
# 终极跨域放行（虽然同源后不再强制需要，但保留以兼容本地调试）
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})

# --- 核心配置区 ---
# 主战场连接信息
NEW_API_BASE = "https://api-tokenmaster.com/v1/chat/completions"
# 请确保这是您在主战场生成的【完整、无星号】的 sk-密钥
NEW_API_KEY = "sk-Yb6fOVUVZHJpbMakOSdT8fPF4sUTTS1GwcJeNkGRczdm1EEK" 
# 前端 HTML 文件名
HTML_FILE = "dream_pro_landing_v33_referral.html"

def _build_cors_response(data, status=200):
    """辅助函数：构建带有完整 CORS 头的响应"""
    response = make_response(jsonify(data), status)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

# --- 路由区 ---

@app.route('/')
def serve_index():
    """【圣殿入口】直接托管并分发前端网页"""
    if os.path.exists(HTML_FILE):
        return send_file(HTML_FILE)
    return f"<h1>Error: {HTML_FILE} not found in root directory.</h1>", 404

@app.route('/api/referral/init', methods=['GET', 'POST', 'OPTIONS'])
def init_referral():
    """初始化接口：握手确认"""
    return _build_cors_response({
        "status": "ready", 
        "msg": "Sanctum Connection Established",
        "version": "v33.2.8"
    })

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    """解梦核心接口：转发请求至主战场"""
    if request.method == 'OPTIONS':
        return _build_cors_response({})
    
    data = request.json
    messages = data.get('messages', [])
    lang = data.get('lang', 'zh')
    
    # 注入 Oracle 预言家系统提示词
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
        # 向主战场发起请求
        response = requests.post(
            NEW_API_BASE,
            headers={
                "Authorization": f"Bearer {NEW_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-reasoner", # 已经在主战场配置了映射
                "messages": [system_prompt] + messages,
                "temperature": 0.7
            },
            timeout=120
        )
        return _build_cors_response(response.json())
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return _build_cors_response({"error": "Ether Connection Flicker", "details": str(e)}, 500)

# --- 启动区 ---

if __name__ == '__main__':
    # 获取 Zeabur 动态分配的端口，默认为 5000
    port = int(os.environ.get("PORT", 5000))
    # 生产环境建议通过 Gunicorn 启动，此处保留 app.run 兼容性
    app.run(host='0.0.0.0', port=port)
