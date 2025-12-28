"""
Модуль для работы с базой данных SQLite.
Здесь находятся функции для создания таблицы, добавления, удаления и получения задач.
"""
import sqlite3
from datetime import datetime
from config import DATABASE_NAME


def init_database():
    """
    Инициализация базы данных.
    Создает таблицу tasks, если она еще не существует.
    Добавляет поле category, если его еще нет (для существующих баз данных).
    """
    # Подключаемся к базе данных (файл будет создан автоматически, если его нет)
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Создаем таблицу tasks с полями:
    # id - уникальный идентификатор задачи (автоинкремент)
    # text - текст задачи
    # user - идентификатор пользователя Telegram
    # category - категория задачи (DataBase, Frontend, Backend, Business)
    # created_at - дата и время создания задачи
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            user INTEGER NOT NULL,
            category TEXT NOT NULL DEFAULT 'Business',
            created_at TEXT NOT NULL
        )
    ''')
    
    # Проверяем, существует ли колонка category (для обновления существующих баз данных)
    cursor.execute("PRAGMA table_info(tasks)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'category' not in columns:
        # Добавляем колонку category, если её нет
        cursor.execute('ALTER TABLE tasks ADD COLUMN category TEXT NOT NULL DEFAULT "Business"')
    
    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()


def add_task(text: str, user_id: int, category: str = "Business") -> int:
    """
    Добавляет новую задачу в базу данных.
    
    Args:
        text: Текст задачи
        user_id: ID пользователя Telegram
        category: Категория задачи (DataBase, Frontend, Backend, Business)
    
    Returns:
        ID созданной задачи
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Получаем текущую дату и время в формате строки
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Вставляем новую задачу в таблицу
    cursor.execute('''
        INSERT INTO tasks (text, user, category, created_at)
        VALUES (?, ?, ?, ?)
    ''', (text, user_id, category, created_at))
    
    # Получаем ID созданной задачи
    task_id = cursor.lastrowid
    
    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()
    
    return task_id


def delete_task(task_id: int, user_id: int) -> bool:
    """
    Удаляет задачу по ID, если она принадлежит пользователю.
    
    Args:
        task_id: ID задачи для удаления
        user_id: ID пользователя Telegram
    
    Returns:
        True если задача была удалена, False если задача не найдена или не принадлежит пользователю
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Удаляем задачу только если она принадлежит пользователю
    cursor.execute('''
        DELETE FROM tasks 
        WHERE id = ? AND user = ?
    ''', (task_id, user_id))
    
    # Проверяем, была ли удалена хотя бы одна строка
    deleted = cursor.rowcount > 0
    
    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()
    
    return deleted


def get_all_tasks(user_id: int = None):
    """
    Получает все задачи из базы данных.
    
    Args:
        user_id: Если указан, возвращает только задачи этого пользователя.
                 Если None, возвращает все задачи.
    
    Returns:
        Список кортежей (id, text, user, category, created_at)
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    if user_id:
        # Получаем задачи конкретного пользователя
        cursor.execute('''
            SELECT id, text, user, category, created_at 
            FROM tasks 
            WHERE user = ?
            ORDER BY id
        ''', (user_id,))
    else:
        # Получаем все задачи
        cursor.execute('''
            SELECT id, text, user, category, created_at 
            FROM tasks 
            ORDER BY id
        ''')
    
    # Получаем все результаты
    tasks = cursor.fetchall()
    
    # Закрываем соединение
    conn.close()
    
    return tasks


def get_tasks_by_category(category: str):
    """
    Получает все задачи по указанной категории.
    
    Args:
        category: Категория задачи (DataBase, Frontend, Backend, Business)
    
    Returns:
        Список кортежей (id, text, user, category, created_at)
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Получаем все задачи указанной категории
    cursor.execute('''
        SELECT id, text, user, category, created_at 
        FROM tasks 
        WHERE category = ?
        ORDER BY id
    ''', (category,))
    
    # Получаем все результаты
    tasks = cursor.fetchall()
    
    # Закрываем соединение
    conn.close()
    
    return tasks


def get_task_by_id(task_id: int):
    """
    Получает задачу по ID.
    
    Args:
        task_id: ID задачи
    
    Returns:
        Кортеж (id, text, user, category, created_at) или None, если задача не найдена
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, text, user, category, created_at 
        FROM tasks 
        WHERE id = ?
    ''', (task_id,))
    
    task = cursor.fetchone()
    
    conn.close()
    
    return task

