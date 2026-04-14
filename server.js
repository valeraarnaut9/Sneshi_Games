const express = require('express');
const tmi = require('tmi.js');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

// Хранилище сообщений (последние 100)
let messages = [];

// Настройки Twitch (замените на свои)
const twitchClient = new tmi.Client({
    options: { debug: false },
    identity: {
        username: 'your_bot_name', // имя вашего бота
        password: 'oauth:ваш_токен' // получите на https://twitchapps.com/tmi/
    },
    channels: ['channel_name'] // имя канала, чей чат читаем
});

// Подключение к Twitch
twitchClient.connect().catch(console.error);

// Обработка сообщений чата
twitchClient.on('message', (channel, tags, message, self) => {
    if (self) return; // игнорируем свои сообщения
    
    const chatMessage = {
        username: tags['display-name'] || tags.username,
        message: message,
        timestamp: new Date().toISOString(),
        color: tags.color || '#FFFFFF',
        badges: tags.badges || {},
        isSubscriber: tags.subscriber || false,
        isMod: tags.mod || false
    };
    
    // Добавляем в начало массива (свежие первыми)
    messages.unshift(chatMessage);
    
    // Ограничиваем размер
    if (messages.length > 100) messages.pop();
    
    console.log(`${chatMessage.username}: ${chatMessage.message}`);
});

// API эндпоинты для Roblox
app.get('/api/messages', (req, res) => {
    const limit = parseInt(req.query.limit) || 20;
    res.json(messages.slice(0, limit));
});

app.get('/api/latest', (req, res) => {
    if (messages.length > 0) {
        res.json(messages[0]);
    } else {
        res.json(null);
    }
});

app.get('/api/health', (req, res) => {
    res.json({ status: 'ok', messages_count: messages.length });
});

// Запуск сервера
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
    console.log(`Twitch bot connecting to channel...`);
});
