from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import re
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)  # Разрешаем запросы от Roblox

# ===== НАСТРОЙКИ =====
API_KEY = "ВАШ_ЛОКАЛЬНЫЙ_КЛЮЧ"  # Замените на свой ключ
CLIENT_ID = "cuuagwn6h9m0wogvkoa657vjdd3..."  # Ваш Client ID
CLIENT_SECRET = "ВАШ_SECRET_КЛЮЧ"  # Получите в Twitch Developer Console

# Хранилище последних сообщений
recent_messages = []
TARGET_USER = "deepins02"

# ===== ПОЛУЧЕНИЕ ТОКЕНА =====
def get_twitch_token():
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
    response = requests.post(url, params=params)
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

# ===== ПОЛУЧЕНИЕ ID ПОЛЬЗОВАТЕЛЯ =====
def get_user_id(username, token):
    url = f"https://api.twitch.tv/helix/users?login={username}"
    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200 and response.json()["data"]:
        return response.json()["data"][0]["id"]
    return None

# ===== ФЕЙКОВЫЕ СООБЩЕНИЯ ДЛЯ ТЕСТА (пока нет реального IRC) =====
# Позже заменим на реальные сообщения из чата
fake_messages = [
    "привет", "как дела?", "ok", "lol", "gg", "wow", "hi", "hey",
    "да", "нет", "круто", "класс", "ой", "ах", "ура"
]

@app.route("/get_chat_messages", methods=["GET"])
def get_chat_messages():
    """Roblox вызывает этот эндпоинт чтобы получить сообщения"""
    key = request.args.get("key")
    
    # Проверка ключа
    if key != API_KEY:
        return jsonify({"error": "NO ACCESS"}), 403
    
    # Для теста возвращаем случайные короткие сообщения (до 3 символов)
    # В реальности здесь будет получение сообщений из чата
    
    # Фильтруем сообщения до 3 символов
    short_messages = [msg for msg in fake_messages if len(msg) <= 3]
    
    # Берем последние 5 коротких сообщений
    if short_messages:
        # Имитируем новые сообщения
        import random
        latest = random.sample(short_messages, min(3, len(short_messages)))
    else:
        latest = ["..."]
    
    return jsonify({
        "success": True,
        "messages": latest,
        "streamer": TARGET_USER
    })

# ===== ЭНДПОИНТ ДЛЯ ПРОВЕРКИ РАБОТОСПОСОБНОСТИ =====
@app.route("/ping", methods=["GET"])
def ping():
    key = request.args.get("key")
    if key == API_KEY:
        return jsonify({"status": "ok", "message": "Server is running"})
    return jsonify({"error": "Invalid key"}), 403

if __name__ == "__main__":
    print(f"Сервер запущен! API_KEY = {API_KEY}")
    print(f"Следим за стримером: {TARGET_USER}")
    app.run(host="0.0.0.0", port=5000, debug=True)
