"""
Модуль для определения состояний (FSM) бота.
Состояния используются для отслеживания, чего бот ожидает от пользователя.
"""
from aiogram.fsm.state import State, StatesGroup


class TaskStates(StatesGroup):
    """
    Группа состояний для работы с задачами.
    """
    # Состояние ожидания текста задачи (после команды /add)
    waiting_for_task_text = State()
    
    # Состояние ожидания выбора категории задачи (после ввода текста задачи)
    waiting_for_category = State()
    
    # Состояние ожидания выбора категории для фильтрации списка (после команды /list_category)
    waiting_for_category_filter = State()
    
    # Состояние ожидания ID задачи для удаления (после команды /delete)
    waiting_for_task_id = State()

