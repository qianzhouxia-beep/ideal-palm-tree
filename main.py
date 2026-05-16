import os

# ... (中间的代码不变)

if __name__ == '__main__':
    # 这一行是灵魂：优先使用 Zeabur 给的端口
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
