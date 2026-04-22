from flask import Flask, request, jsonify
from flask_cors import CORS
import socket
import re
import threading
import time
from datetime import datetime, timedelta
import random

app = Flask(__name__)
CORS(app)

# ===== НАСТРОЙКИ =====
API_KEY = "ВАШ_ЛОКАЛЬНЫЙ_КЛЮЧ"  # Замените на свой ключ
CLIENT_ID = "cuuagwn6h9m0wogvkoa657vjdd3..."  # Ваш Client ID
CLIENT_SECRET = "ВАШ_SECRET_КЛЮЧ"

# Настройки для IRC
TARGET_USER = "deepins02"  # Стример за которым следим
BOT_NICKNAME = "justinfan12345"  # Анонимный ник для чтения чата (не требует регистрации)
BOT_TOKEN = ""  # Для анонимного чтения оставляем пустым

# Хранилище сообщений (максимум 50 последних)
chat_messages = []
MAX_MESSAGES = 50

# ===== ПОЛУЧЕНИЕ OAUTH ТОКЕНА ДЛЯ IRC (если нужен) =====
def get_irc_token():
    """Получает токен для IRC подключения (только если у вас есть аккаунт бота)"""
    if BOT_TOKEN:
        return BOT_TOKEN
    
    # Для анонимного чтения используем фейковый ник
    return None

# ===== IRC КЛИЕНТ ДЛЯ ЧТЕНИЯ ЧАТА =====
class TwitchChatReader:
    def __init__(self, channel, nickname="justinfan12345", token=None):
        self.channel = channel.lower()
        self.nickname = nickname
        self.token = token
        self.sock = None
        self.running = False
        self.message_callback = None
        
    def set_callback(self, callback):
        """Устанавливает функцию, которая будет вызываться при новом сообщении"""
        self.message_callback = callback
    
    def connect(self):
        """Подключается к Twitch IRC"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect(("irc.chat.twitch.tv", 6667))
            
            # Отправка команд для подключения
            self.send_command(f"PASS {self.token}" if self.token else "PASS dummy")
            self.send_command(f"NICK {self.nickname}")
            self.send_command(f"JOIN #{self.channel}")
            
            self.running = True
            print(f"[IRC] Подключен к чату #{self.channel}")
            return True
        except Exception as e:
            print(f"[IRC] Ошибка подключения: {e}")
            return False
    
    def send_command(self, cmd):
        """Отправляет команду в IRC"""
        if self.sock:
            self.sock.send(f"{cmd}\r\n".encode("utf-8"))
    
    def receive_messages(self):
        """Основной цикл приема сообщений"""
        buffer = ""
        while self.running and self.sock:
            try:
                data = self.sock.recv(4096).decode("utf-8", errors="ignore")
                if not data:
                    break
                    
                buffer += data
                lines = buffer.split("\r\n")
                buffer = lines[-1]
                
                for line in lines[:-1]:
                    self.process_line(line)
                    
            except Exception as e:
                print(f"[IRC] Ошибка приема: {e}")
                break
    
    def process_line(self, line):
        """Обрабатывает одну строку от IRC сервера"""
        # Ответ на PING (keep-alive)
        if line.startswith("PING"):
            self.send_command(f"PONG {line.split()[1]}")
            return
        
        # Парсинг сообщения чата
        # Формат: :username!username@username.tmi.twitch.tv PRIVMSG #channel :message
        privmsg_match = re.search(r":([^!]+)!.*PRIVMSG #\S+ :(.*)", line)
        
        if privmsg_match:
            username = privmsg_match.group(1)
            message = privmsg_match.group(2).strip()
            
            # Фильтруем сообщения только от нужного стримера
            if username.lower() == self.channel:
                if self.message_callback:
                    self.message_callback(username, message)
                print(f"[ЧАТ] {username}: {message}")
    
    def stop(self):
        """Останавливает подключение"""
        self.running = False
        if self.sock:
            self.send_command("PART #" + self.channel)
            self.sock.close()
            print("[IRC] Отключен от чата")

# ===== ГЛОБАЛЬНЫЙ IRC КЛИЕНТ =====
irc_client = None

def on_new_message(username, message):
    """Вызывается при новом сообщении от стримера"""
    global chat_messages
    
    # Фильтр: только сообщения до 3 символов
    if len(message) <= 3:
        message_data = {
            "username": username,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "length": len(message)
        }
        
        chat_messages.insert(0, message_data)
        
        # Ограничиваем размер хранилища
        if len(chat_messages) > MAX_MESSAGES:
            chat_messages.pop()
        
        print(f"[НОВОЕ] {username}: '{message}' ({len(message)} символов)")

# ===== ЗАПУСК IRC В ОТДЕЛЬНОМ ПОТОКЕ =====
def start_irc_client():
    global irc_client
    irc_client = TwitchChatReader(TARGET_USER, BOT_NICKNAME, BOT_TOKEN)
    irc_client.set_callback(on_new_message)
    
    while True:
        if irc_client.connect():
            irc_client.receive_messages()
        else:
            print("[IRC] Переподключение через 5 секунд...")
            time.sleep(5)

# ===== FLASK ЭНДПОИНТЫ =====
@app.route("/get_chat_messages", methods=["GET"])
def get_chat_messages():
    """Roblox вызывает этот эндпоинт для получения коротких сообщений"""
    key = request.args.get("key")
    
    # Проверка ключа
    if key != API_KEY:
        return jsonify({"error": "NO ACCESS"}), 403
    
    # Получаем последние 5 коротких сообщений
    short_messages = [msg["message"] for msg in chat_messages if msg["length"] <= 3]
    latest_messages = short_messages[:5]  # Последние 5 сообщений
    
    return jsonify({
        "success": True,
        "messages": latest_messages,
        "streamer": TARGET_USER,
        "total_short_messages": len(short_messages)
    })

@app.route("/get_latest_message", methods=["GET"])
def get_latest_message():
    """Возвращает только последнее короткое сообщение"""
    key = request.args.get("key")
    
    if key != API_KEY:
        return jsonify({"error": "NO ACCESS"}), 403
    
    # Ищем последнее короткое сообщение
    for msg in chat_messages:
        if msg["length"] <= 3:
            return jsonify({
                "success": True,
                "message": msg["message"],
                "username": msg["username"],
                "timestamp": msg["timestamp"]
            })
    
    return jsonify({
        "success": True,
        "message": "...",
        "username": None
    })

@app.route("/ping", methods=["GET"])
def ping():
    key = request.args.get("key")
    if key == API_KEY:
        return jsonify({
            "status": "ok",
            "connected": irc_client is not None and irc_client.running,
            "messages_count": len(chat_messages)
        })
    return jsonify({"error": "Invalid key"}), 403

@app.route("/stats", methods=["GET"])
def stats():
    """Статистика для отладки"""
    key = request.args.get("key")
    if key != API_KEY:
        return jsonify({"error": "NO ACCESS"}), 403
    
    short_msgs = [m for m in chat_messages if m["length"] <= 3]
    return jsonify({
        "total_messages": len(chat_messages),
        "short_messages": len(short_msgs),
        "latest_short": short_msgs[:3] if short_msgs else []
    })

# ===== ЗАПУСК =====
if __name__ == "__main__":
    # Запускаем IRC клиент в отдельном потоке
    irc_thread = threading.Thread(target=start_irc_client, daemon=True)
    irc_thread.start()
    
    print(f"=== SERVER STARTED ===")
    print(f"API_KEY: {API_KEY}")
    print(f"Следим за стримером: {TARGET_USER}")
    print(f"Фильтр: только сообщения до 3 символов")
    print(f"Сервер на http://localhost:5000")
    print("======================")
    
    # Запускаем Flask сервер
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
