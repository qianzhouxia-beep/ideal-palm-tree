if __name__ == '__main__':
    # 动态获取 Zeabur 注入的 PORT 环境变量，默认 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
