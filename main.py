# main.py - Version: v33.2.11 (FULL PRODUCTION READY)
import os
import requests
from flask import Flask, request, jsonify, make_response, send_file
from flask_cors import CORS

app = Flask(__name__)
# 禁用路径严格模式，解决末尾斜杠导致的 405/404 问题
app.url_map.strict_slashes = False
# 开启全域跨域支持，确保本地测试和生产环境无缝衔接
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})

# --- 核心配置：圣殿能源中心 ---
NEW_API_BASE = "https://api-tokenmaster.com/v1/chat/completions"
# 使用您刚刚在游乐场测试通过的【Mirror API】黄金密钥
NEW_API_KEY = "sk-biaE1BokgWzky0VkQwX3DuiVCThyVjIlf9BxejJSGi3U0M8j" 
# 前端文件：确保此文件与 main.py 处于同一 GitHub 目录下
HTML_FILE = "dream_pro_landing_v33_referral.html"

def _build_cors_response(data, status=200):
    """辅助函数：确保每一个响应都带有干净的 CORS 头"""
    response = make_response(jsonify(data), status)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

# --- 业务路由 ---

@app.route('/')
def serve_index():
    """托管前端：访问域名直接打开解梦网页"""
    if os.path.exists(HTML_FILE):
        return send_file(HTML_FILE)
    return f"<h1>Oracle Error</h1><p>File {HTML_FILE} missing in root.</p>", 404

@app.route('/api/referral/init', methods=['GET', 'POST', 'OPTIONS'])
def init_referral():
    """握手接口：确认前端与后端已连接"""
    return _build_cors_response({
        "status": "ready", 
        "msg": "Sanctum Connection Stable",
        "version": "v33.2.11"
    })

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    """核心接口：接收梦境，清洗数据，返回解梦"""
    if request.method == 'OPTIONS':
        return _build_cors_response({})
    
    data = request.json
    messages = data.get('messages', [])
    lang = data.get('lang', 'zh')
    
    # 预言家身份注入
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
                "model": "deepseek-reasoner",
                "messages": [system_prompt] + messages,
                "temperature": 0.7
            },
            timeout=120
        )
        
        raw_res = response.json()
        
        # --- 深度逻辑修复：处理 Reasoner 模型的特殊格式 ---
        # 如果主战场返回了数据
        if "choices" in raw_res and len(raw_res["choices"]) > 0:
            msg_obj = raw_res["choices"][0]["message"]
            content = msg_obj.get("content", "")
            
            # 如果 content 为空（R1有时会将内容放在 reasoning_content 中）
            # 或者为了确保前端展示，我们提取最核心的内容
            if not content and "reasoning_content" in msg_obj:
                content = msg_obj["reasoning_content"]
            
            # 重新打包成前端 HTML 认识的标准格式
            clean_res = {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": content
                        }
                    }
                ]
            }
            return _build_cors_response(clean_res)
            
        return _build_cors_response(raw_res)

    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        return _build_cors_response({"error": "Ether Connection Flicker", "details": str(e)}, 500)

# --- 启动配置 ---

if __name__ == '__main__':
    # 适配 Zeabur 端口
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
