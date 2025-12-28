"""
Модуль конфигурации для Telegram бота.
Здесь хранятся настройки приложения, такие как токен бота.
"""
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()

# Токен бота получаем из переменной окружения BOT_TOKEN
# Его можно получить у @BotFather в Telegram
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Имя файла базы данных
DATABASE_NAME = 'tasks.db'

