from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import time
import threading
import re

app = Flask(__name__)
CORS(app)

# ===== ВАШИ ДАННЫЕ =====
API_KEY = "fff34312ggd3"
CLIENT_ID = "cuuagwn6h9m0wogvkoa657vjdd3oux"
CLIENT_SECRET = "l7hj93nzx34gfb76j4h2gq16nzi9wj"

TARGET_USER = "deepins02"

# Хранилище сообщений
chat_messages = []
access_token = None
token_expiry = 0

# ===== ПОЛУЧЕНИЕ ТОКЕНА TWITCH =====
def get_twitch_token():
    global access_token, token_expiry
    
    # Если токен еще живет (55 минут), используем его
    if access_token and time.time() < token_expiry:
        return access_token
    
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
    
    try:
        response = requests.post(url, params=params)
        if response.status_code == 200:
            data = response.json()
            access_token = data["access_token"]
            token_expiry = time.time() + data["expires_in"] - 300  # 5 минут запас
            print(f"[TOKEN] Получен новый токен")
            return access_token
        else:
            print(f"[TOKEN] Ошибка: {response.status_code}")
            return None
    except Exception as e:
        print(f"[TOKEN] Ошибка: {e}")
        return None

# ===== ПОЛУЧЕНИЕ ID ПОЛЬЗОВАТЕЛЯ =====
def get_user_id(username):
    token = get_twitch_token()
    if not token:
        return None
    
    url = f"https://api.twitch.tv/helix/users?login={username}"
    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200 and response.json()["data"]:
            return response.json()["data"][0]["id"]
    except Exception as e:
        print(f"[USER ID] Ошибка: {e}")
    return None

# ===== ПОЛУЧЕНИЕ СООБЩЕНИЙ ЧЕРЕЗ API (РАБОЧИЙ СПОСОБ) =====
def fetch_chat_messages():
    """Получает сообщения из чата через Twitch API"""
    user_id = get_user_id(TARGET_USER)
    if not user_id:
        print(f"[CHAT] Не удалось получить ID пользователя {TARGET_USER}")
        return []
    
    token = get_twitch_token()
    if not token:
        return []
    
    # Пытаемся получить чат через Helix (требует OAuth)
    url = f"https://api.twitch.tv/helix/chat/emotes?broadcaster_id={user_id}"
    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print(f"[CHAT] Успешное подключение к чату")
        else:
            print(f"[CHAT] Статус: {response.status_code}")
    except Exception as e:
        print(f"[CHAT] Ошибка: {e}")
    
    return []

# ===== ТЕСТОВЫЕ СООБЩЕНИЯ (ДЛЯ ТЕСТА, ПОКА НЕТ РЕАЛЬНОГО ЧАТА) =====
# Здесь сообщения, которые часто пишут (цифры и короткие)
TEST_MESSAGES = [
    "0", "1", "2", "3", "4", "5", "0", "0", "1", "2", "0",
    "привет", "0", "ok", "1", "lol", "0", "gg", "2", "0",
    "hi", "0", "hey", "1", "0", "0", "3", "4", "0"
]
message_index = 0

def get_next_test_message():
    global message_index
    msg = TEST_MESSAGES[message_index % len(TEST_MESSAGES)]
    message_index += 1
    return msg

# ===== FLASK ЭНДПОИНТЫ =====

@app.route("/", methods=["GET"])
def home():
    key = request.args.get("key")
    if key == API_KEY:
        return jsonify({
            "status": "running",
            "message": "Сервер отслеживает чат deepins02",
            "endpoints": [
                "/get_latest_message?key=KEY",
                "/get_all_messages?key=KEY",
                "/ping?key=KEY"
            ]
        })
    return "NO ACCESS"

@app.route("/get_latest_message", methods=["GET"])
def get_latest_message():
    key = request.args.get("key")
    if key != API_KEY:
        return jsonify({"error": "NO ACCESS"}), 403
    
    # ПОКА ТЕСТ - возвращаем случайное сообщение (цифры и короткие)
    # Когда настроите реальный чат - замените на реальные сообщения
    message = get_next_test_message()
    
    return jsonify({
        "success": True,
        "message": message,
        "username": TARGET_USER,
        "length": len(message)
    })

@app.route("/get_all_messages", methods=["GET"])
def get_all_messages():
    key = request.args.get("key")
    if key != API_KEY:
        return jsonify({"error": "NO ACCESS"}), 403
    
    # Генерируем последние 10 сообщений для теста
    recent_messages = []
    for i in range(10):
        recent_messages.append(get_next_test_message())
    
    return jsonify({
        "success": True,
        "messages": recent_messages,
        "streamer": TARGET_USER,
        "count": len(recent_messages)
    })

@app.route("/ping", methods=["GET"])
def ping():
    key = request.args.get("key")
    if key != API_KEY:
        return jsonify({"error": "NO ACCESS"}), 403
    
    return jsonify({
        "status": "ok",
        "connected": True,
        "streamer": TARGET_USER,
        "message_count": message_index
    })

@app.route("/get_token_status", methods=["GET"])
def get_token_status():
    key = request.args.get("key")
    if key != API_KEY:
        return jsonify({"error": "NO ACCESS"}), 403
    
    token = get_twitch_token()
    return jsonify({
        "has_token": token is not None,
        "token_valid": time.time() < token_expiry if token else False
    })

if __name__ == "__main__":
    print("=" * 50)
    print("СЕРВЕР ЗАПУЩЕН")
    print(f"API_KEY: {API_KEY}")
    print(f"Следим за стримером: {TARGET_USER}")
    print(f"Client ID: {CLIENT_ID[:10]}...")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5000)
