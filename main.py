import os
import json
import time
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

NEW_API_BASE = "https://api-tokenmaster.com/v1/chat/completions"
NEW_API_KEY = "sk-Sef-9i7k]1zjicK6Nv" 

@app.route('/')
def home():
    return jsonify({"status": "Subconscious Mirror Oracle is Live", "version": "v33.2"})

@app.route('/api/chat', methods=['POST'])
def chat():
    # ... (保持之前的 AI 逻辑)
    return jsonify({"message": "Oracle Ready"})

if __name__ == '__main__':
    # 这里的端口逻辑是为了本地调试，线上会被 gunicorn 接管
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
