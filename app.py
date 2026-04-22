from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import time
import random

app = Flask(__name__)
CORS(app)

# ===== ВАШИ ДАННЫЕ =====
API_KEY = "fff34312ggd3"
CLIENT_ID = "cuuagwn6h9m0wogvkoa657vjdd3oux"
CLIENT_SECRET = "l7hj93nzx34gfb76j4h2gq16nzi9wj"
TARGET_USER = "deepins02"

# Хранилище сообщений
messages_cache = []
last_fetch_time = 0
access_token = None
token_expiry = 0

# ===== ПОЛУЧЕНИЕ ТОКЕНА TWITCH =====
def get_twitch_token():
    global access_token, token_expiry
    
    if access_token and time.time() < token_expiry:
        return access_token
    
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
    
    try:
        response = requests.post(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            access_token = data["access_token"]
            token_expiry = time.time() + data["expires_in"] - 300
            print(f"✅ Токен получен")
            return access_token
    except Exception as e:
        print(f"❌ Ошибка токена: {e}")
    return None

# ===== ПОЛУЧЕНИЕ ID СТРИМЕРА =====
def get_user_id():
    token = get_twitch_token()
    if not token:
        return None
    
    url = f"https://api.twitch.tv/helix/users?login={TARGET_USER}"
    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200 and response.json()["data"]:
            user_id = response.json()["data"][0]["id"]
            print(f"✅ ID {TARGET_USER}: {user_id}")
            return user_id
    except Exception as e:
        print(f"❌ Ошибка ID: {e}")
    return None

# ===== ПОЛУЧЕНИЕ СООБЩЕНИЙ (РЕАЛЬНЫХ) =====
def fetch_real_messages():
    """Пытается получить реальные сообщения из чата"""
    global messages_cache
    
    # Способ 1: Через сторонний API (работает иногда)
    try:
        url = f"https://api.ivr.fi/twitch/logs/{TARGET_USER}?limit=5"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                messages = []
                for msg in data:
                    text = msg.get("message", "")
                    if text and len(text) <= 3:  # Только короткие сообщения
                        messages.append(text)
                if messages:
                    return messages
    except:
        pass
    
    # Способ 2: Через другой API
    try:
        url = f"https://decapi.me/twitch/latest/{TARGET_USER}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            text = response.text.strip()
            if text and len(text) <= 3:
                return [text]
    except:
        pass
    
    # Если ничего не работает - возвращаем None
    return None

# ===== ФЕЙКОВЫЕ СООБЩЕНИЯ (ДЛЯ ТЕСТА) =====
# Когда реальные сообщения не доступны, используем числа
fake_numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

# ===== ЭНДПОИНТЫ =====

@app.route("/", methods=["GET"])
def home():
    key = request.args.get("key")
    if key == API_KEY:
        return jsonify({
            "status": "running",
            "streamer": TARGET_USER,
            "message": "Сервер работает"
        })
    return "NO ACCESS"

@app.route("/get_latest_message", methods=["GET"])
def get_latest_message():
    key = request.args.get("key")
    if key != API_KEY:
        return jsonify({"error": "NO ACCESS"}), 403
    
    # Пытаемся получить реальные сообщения
    real_msgs = fetch_real_messages()
    
    if real_msgs and len(real_msgs) > 0:
        # Берем последнее реальное сообщение
        message = real_msgs[0]
        return jsonify({
            "success": True,
            "message": message,
            "username": TARGET_USER,
            "type": "real"
        })
    else:
        # Если реальных нет - возвращаем случайное число (для теста)
        fake_msg = random.choice(fake_numbers)
        return jsonify({
            "success": True,
            "message": fake_msg,
            "username": TARGET_USER,
            "type": "test"
        })

@app.route("/get_chat_messages", methods=["GET"])
def get_chat_messages():
    key = request.args.get("key")
    if key != API_KEY:
        return jsonify({"error": "NO ACCESS"}), 403
    
    # Пытаемся получить реальные сообщения
    real_msgs = fetch_real_messages()
    
    if real_msgs and len(real_msgs) > 0:
        return jsonify({
            "success": True,
            "messages": real_msgs[:5],
            "streamer": TARGET_USER,
            "type": "real"
        })
    else:
        # Тестовые числа
        return jsonify({
            "success": True,
            "messages": fake_numbers[:5],
            "streamer": TARGET_USER,
            "type": "test"
        })

@app.route("/ping", methods=["GET"])
def ping():
    key = request.args.get("key")
    if key != API_KEY:
        return jsonify({"error": "NO ACCESS"}), 403
    
    return jsonify({
        "status": "ok",
        "connected": True,
        "streamer": TARGET_USER
    })

if __name__ == "__main__":
    print("=" * 50)
    print(f"СЕРВЕР ЗАПУЩЕН")
    print(f"Стример: {TARGET_USER}")
    print(f"API_KEY: {API_KEY}")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5000)
