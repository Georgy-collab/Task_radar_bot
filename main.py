"""
Главный файл приложения - точка входа в программу.
Здесь происходит инициализация бота и запуск приложения.
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database import init_database
from handlers import router

# Настраиваем логирование для отслеживания работы бота
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """
    Главная функция приложения.
    Инициализирует бота, регистрирует обработчики и запускает polling.
    """
    # Проверяем, что токен бота установлен
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN не установлен! Создайте файл .env и добавьте BOT_TOKEN=ваш_токен")
        return
    
    # Инициализируем базу данных (создаем таблицу, если её нет)
    init_database()
    logger.info("База данных инициализирована")
    
    # Создаем объект бота с настройками по умолчанию
    # ParseMode.HTML позволяет использовать HTML-разметку в сообщениях
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Создаем хранилище для состояний (FSM)
    # MemoryStorage хранит состояния в памяти (временное хранилище)
    storage = MemoryStorage()
    
    # Создаем диспетчер для обработки сообщений с хранилищем состояний
    dp = Dispatcher(storage=storage)
    
    # Регистрируем роутер с обработчиками команд
    dp.include_router(router)
    
    logger.info("Бот запущен и готов к работе!")
    
    # Запускаем polling (процесс получения и обработки обновлений от Telegram)
    await dp.start_polling(bot)


if __name__ == "__main__":
    """
    Точка входа в программу.
    Запускает асинхронную функцию main().
    """
    try:
        # Запускаем главную функцию
        asyncio.run(main())
    except KeyboardInterrupt:
        # Если пользователь нажал Ctrl+C, корректно завершаем работу
        logger.info("Бот остановлен пользователем")

