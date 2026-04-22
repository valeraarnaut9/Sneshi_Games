from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import time
import re

app = Flask(__name__)
CORS(app)

# ===== ВАШИ ДАННЫЕ =====
API_KEY = "fff34312ggd3"
CLIENT_ID = "cuuagwn6h9m0wogvkoa657vjdd3oux"
CLIENT_SECRET = "l7hj93nzx34gfb76j4h2gq16nzi9wj"
TARGET_USER = "deepins02"

# Хранилище реальных сообщений
real_messages = []
access_token = None
token_expiry = 0
broadcaster_id = None

# ===== ПОЛУЧЕНИЕ ТОКЕНА =====
def get_token():
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
        response = requests.post(url, params=params)
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
    global broadcaster_id
    
    if broadcaster_id:
        return broadcaster_id
    
    token = get_token()
    if not token:
        return None
    
    url = f"https://api.twitch.tv/helix/users?login={TARGET_USER}"
    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200 and response.json()["data"]:
            broadcaster_id = response.json()["data"][0]["id"]
            print(f"✅ ID {TARGET_USER}: {broadcaster_id}")
            return broadcaster_id
    except Exception as e:
        print(f"❌ Ошибка ID: {e}")
    return None

# ===== ПОЛУЧЕНИЕ СООБЩЕНИЙ ЧЕРЕЗ CHAT BADGES (единственное, что доступно без OAuth пользователя) =====
# ВНИМАНИЕ: Twitch API не дает читать сообщения чата без подключения к IRC или WebSocket
# Этот метод возвращает только бейджики, а не текст сообщений

@app.route("/get_latest_message", methods=["GET"])
def get_latest_message():
    key = request.args.get("key")
    if key != API_KEY:
        return jsonify({"error": "NO ACCESS"}), 403
    
    # ПЫТАЕМСЯ ПОЛУЧИТЬ РЕАЛЬНЫЕ СООБЩЕНИЯ
    # НО Twitch API НЕ ПОЗВОЛЯЕТ читать чат через HTTP!
    # Поэтому возвращаем заглушку с объяснением
    
    return jsonify({
        "success": False,
        "message": "?",
        "error": "Twitch API не позволяет читать чат через HTTP. Нужен IRC или WebSocket.",
        "solution": "Используйте альтернативный сервер с поддержкой IRC (не Render.com)"
    })

@app.route("/ping", methods=["GET"])
def ping():
    key = request.args.get("key")
    if key != API_KEY:
        return jsonify({"error": "NO ACCESS"}), 403
    
    return jsonify({
        "status": "ok",
        "note": "Для чтения чата нужен сервер с поддержкой WebSocket/IRC",
        "render_com_blocks_ports": True
    })

@app.route("/", methods=["GET"])
def home():
    key = request.args.get("key")
    if key == API_KEY:
        return jsonify({
            "status": "running",
            "warning": "Twitch API не позволяет читать сообщения чата через HTTP",
            "solution": "Используйте IRC или WebSocket (Render.com не подходит)"
        })
    return "NO ACCESS"

if __name__ == "__main__":
    print("=" * 50)
    print("⚠️ ВАЖНОЕ ПРЕДУПРЕЖДЕНИЕ:")
    print("Twitch API НЕ позволяет читать сообщения чата")
    print("через обычные HTTP запросы.")
    print("")
    print("Для чтения чата нужно:")
    print("1. IRC подключение (порт 6667)")
    print("2. WebSocket подключение")
    print("3. Сторонний сервис")
    print("")
    print("Render.com НЕ поддерживает эти протоколы")
    print("на бесплатном тарифе.")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5000)
