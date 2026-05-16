# main.py - Version: v33.2.11 (SMART FORMATTER)
@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        return _build_cors_response({})
    
    data = request.json
    try:
        response = requests.post(
            NEW_API_BASE,
            headers={"Authorization": f"Bearer {NEW_API_KEY}"},
            json={
                "model": "deepseek-reasoner",
                "messages": data.get('messages', []),
                "temperature": 0.7
            },
            timeout=120
        )
        res_json = response.json()
        
        # --- 关键修正：确保网页能读到内容 ---
        # 如果是 reasoner 模型，我们要把 content 提取出来
        if "choices" in res_json:
            content = res_json["choices"][0]["message"].get("content", "")
            # 如果 content 为空，尝试取推理内容（虽然不建议，但作为兜底）
            if not content:
                content = res_json["choices"][0]["message"].get("reasoning_content", "Oracle is thinking deep...")
            
            # 重新封装成网页认识的格式
            return _build_cors_response({"choices": [{"message": {"content": content}}]})
            
        return _build_cors_response(res_json)
    except Exception as e:
        return _build_cors_response({"error": str(e)}, 500)
