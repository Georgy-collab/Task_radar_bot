"""
Модуль с обработчиками команд для Telegram бота.
Здесь находятся функции, которые обрабатывают команды от пользователей.
"""
import csv
import io
from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from database import add_task, delete_task, get_all_tasks, get_tasks_by_category
from states import TaskStates
from keyboard import get_category_keyboard, get_category_filter_keyboard

# Создаем роутер для обработчиков команд
router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """
    Обработчик команды /start.
    Отправляет приветственное сообщение с описанием доступных команд.
    Также сбрасывает текущее состояние пользователя.
    """
    # Сбрасываем состояние (на случай, если пользователь был в процессе добавления/удаления задачи)
    await state.clear()
    
    welcome_text = (
        "👋 Привет! Я бот для управления задачами команды.\n\n"
        "Доступные команды:\n"
        "/add - Добавить новую задачу\n"
        "/delete - Удалить задачу по ID\n"
        "/list - Показать все задачи\n"
        "/list_category - Показать задачи по категории\n"
        "/list_csv - Экспортировать задачи в CSV файл\n\n"
        "Начните с команды /add для добавления первой задачи!"
    )
    await message.answer(welcome_text)


@router.message(Command("add"))
async def cmd_add(message: Message, state: FSMContext):
    """
    Обработчик команды /add.
    Устанавливает состояние ожидания текста задачи.
    """
    # Устанавливаем состояние ожидания текста задачи
    await state.set_state(TaskStates.waiting_for_task_text)
    
    await message.answer(
        "📝 Введите текст задачи:\n"
        "(Для отмены отправьте /start или любую другую команду)"
    )


@router.message(Command("delete"))
async def cmd_delete(message: Message, state: FSMContext):
    """
    Обработчик команды /delete.
    Устанавливает состояние ожидания ID задачи для удаления.
    """
    # Устанавливаем состояние ожидания ID задачи
    await state.set_state(TaskStates.waiting_for_task_id)
    
    await message.answer(
        "🗑️ Введите ID задачи для удаления:\n"
        "(Для отмены отправьте /start или любую другую команду)"
    )


@router.message(Command("list"))
async def cmd_list(message: Message, state: FSMContext):
    """
    Обработчик команды /list.
    Показывает все задачи команды в виде списка с указанием автора каждой задачи.
    """
    # Сбрасываем состояние (команда прерывает процесс добавления/удаления)
    await state.clear()
    
    # Получаем все задачи команды (не только текущего пользователя)
    tasks = get_all_tasks(user_id=None)
    
    if not tasks:
        # Если задач нет
        await message.answer("📋 В команде пока нет задач. Добавьте первую задачу командой /add")
        return
    
    # Формируем текст со списком задач
    tasks_text = "📋 Задачи команды:\n\n"
    
    # Получаем информацию о пользователях для отображения имен
    user_info_cache = {}
    
    # Иконки для категорий
    category_icons = {
        "DataBase": "💾",
        "Frontend": "🎨",
        "Backend": "⚙️",
        "Business": "💼"
    }
    
    for task_id, text, user_id, category, created_at in tasks:
        # Получаем информацию о пользователе
        if user_id not in user_info_cache:
            try:
                # Пытаемся получить информацию о пользователе через бота
                chat = await message.bot.get_chat(user_id)
                # Формируем имя пользователя: сначала пробуем полное имя, потом username, потом ID
                if chat.first_name:
                    user_name = f"{chat.first_name}"
                    if chat.last_name:
                        user_name += f" {chat.last_name}"
                    if chat.username:
                        user_name += f" (@{chat.username})"
                elif chat.username:
                    user_name = f"@{chat.username}"
                else:
                    user_name = f"Пользователь {user_id}"
                user_info_cache[user_id] = user_name
            except Exception:
                # Если не удалось получить информацию (пользователь не взаимодействовал с ботом), используем ID
                user_info_cache[user_id] = f"Пользователь {user_id}"
        
        user_name = user_info_cache[user_id]
        
        # Определяем иконку в зависимости от того, принадлежит ли задача текущему пользователю
        icon = "✅" if user_id == message.from_user.id else "📝"
        
        # Получаем иконку категории
        category_icon = category_icons.get(category, "📋")
        
        tasks_text += f"{icon} Задача #{task_id}\n"
        tasks_text += f"   Текст: {text}\n"
        tasks_text += f"   Категория: {category_icon} {category}\n"
        tasks_text += f"   Автор: 👤 {user_name}\n"
        tasks_text += f"   Создано: 📅 {created_at}\n"
        tasks_text += "─" * 30 + "\n"
    
    # Отправляем список задач
    # Если сообщение слишком длинное, Telegram разобьет его на части
    await message.answer(tasks_text)


@router.message(Command("list_category"))
async def cmd_list_category(message: Message, state: FSMContext):
    """
    Обработчик команды /list_category.
    Просит пользователя выбрать категорию для фильтрации списка задач.
    """
    # Сбрасываем состояние (команда прерывает процесс добавления/удаления)
    await state.clear()
    
    # Устанавливаем состояние ожидания выбора категории для фильтрации
    await state.set_state(TaskStates.waiting_for_category_filter)
    
    # Отправляем сообщение с кнопками выбора категории
    await message.answer(
        "📋 Выберите категорию для просмотра задач:",
        reply_markup=get_category_filter_keyboard()
    )


@router.callback_query(StateFilter(TaskStates.waiting_for_category_filter), F.data.startswith("filter_category_"))
async def process_category_filter(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик выбора категории для фильтрации списка задач.
    Вызывается когда пользователь нажимает кнопку с категорией при команде /list_category.
    """
    # Извлекаем категорию из callback_data (format: "filter_category_DataBase")
    category = callback.data.replace("filter_category_", "")
    
    # Сбрасываем состояние
    await state.clear()
    
    # Получаем задачи по выбранной категории
    tasks = get_tasks_by_category(category)
    
    if not tasks:
        # Если задач нет
        await callback.message.edit_text(
            f"📋 В категории '{category}' пока нет задач."
        )
        await callback.answer()
        return
    
    # Формируем текст со списком задач
    tasks_text = f"📋 Задачи категории {category}:\n\n"
    
    # Получаем информацию о пользователях для отображения имен
    user_info_cache = {}
    
    # Иконки для категорий
    category_icons = {
        "DataBase": "💾",
        "Frontend": "🎨",
        "Backend": "⚙️",
        "Business": "💼"
    }
    
    category_icon = category_icons.get(category, "📋")
    
    for task_id, text, user_id, task_category, created_at in tasks:
        # Получаем информацию о пользователе
        if user_id not in user_info_cache:
            try:
                # Пытаемся получить информацию о пользователе через бота
                chat = await callback.message.bot.get_chat(user_id)
                # Формируем имя пользователя: сначала пробуем полное имя, потом username, потом ID
                if chat.first_name:
                    user_name = f"{chat.first_name}"
                    if chat.last_name:
                        user_name += f" {chat.last_name}"
                    if chat.username:
                        user_name += f" (@{chat.username})"
                elif chat.username:
                    user_name = f"@{chat.username}"
                else:
                    user_name = f"Пользователь {user_id}"
                user_info_cache[user_id] = user_name
            except Exception:
                # Если не удалось получить информацию (пользователь не взаимодействовал с ботом), используем ID
                user_info_cache[user_id] = f"Пользователь {user_id}"
        
        user_name = user_info_cache[user_id]
        
        # Определяем иконку в зависимости от того, принадлежит ли задача текущему пользователю
        icon = "✅" if user_id == callback.from_user.id else "📝"
        
        tasks_text += f"{icon} Задача #{task_id}\n"
        tasks_text += f"   Текст: {text}\n"
        tasks_text += f"   Категория: {category_icon} {task_category}\n"
        tasks_text += f"   Автор: 👤 {user_name}\n"
        tasks_text += f"   Создано: 📅 {created_at}\n"
        tasks_text += "─" * 30 + "\n"
    
    # Редактируем сообщение с кнопками, заменяя его на список задач
    await callback.message.edit_text(tasks_text)
    
    # Подтверждаем обработку callback
    await callback.answer()


@router.message(Command("list_csv"))
async def cmd_list_csv(message: Message, state: FSMContext):
    """
    Обработчик команды /list_csv.
    Экспортирует все задачи пользователя в CSV файл и отправляет его пользователю.
    """
    # Сбрасываем состояние (команда прерывает процесс добавления/удаления)
    await state.clear()
    
    # Получаем все задачи текущего пользователя
    tasks = get_all_tasks(user_id=message.from_user.id)
    
    if not tasks:
        await message.answer(
            "📋 У вас пока нет задач для экспорта. "
            "Добавьте первую задачу командой /add"
        )
        return
    
    # Создаем CSV файл в памяти
    # Используем точку с запятой (;) как разделитель для лучшей совместимости с Excel
    csv_buffer = io.StringIO()
    csv_writer = csv.writer(csv_buffer, delimiter=';')
    
    # Записываем заголовки столбцов
    csv_writer.writerow(['ID', 'Текст', 'Категория', 'Пользователь', 'Дата создания'])
    
    # Записываем задачи (task содержит: id, text, user, category, created_at)
    # Переставляем порядок для CSV: id, text, category, user, created_at
    for task in tasks:
        task_id, text, user_id, category, created_at = task
        csv_writer.writerow([task_id, text, category, user_id, created_at])
    
    # Преобразуем текст в байты (UTF-8 с BOM для правильного отображения в Excel)
    csv_bytes = csv_buffer.getvalue().encode('utf-8-sig')
    
    # В aiogram 3.x нужно использовать BufferedInputFile для отправки файлов из памяти
    # Создаем BufferedInputFile из байтов
    document = BufferedInputFile(csv_bytes, filename='tasks.csv')
    
    # Отправляем CSV файл пользователю
    await message.answer_document(
        document,
        caption="📊 Ваши задачи в формате CSV"
    )


@router.message(StateFilter(TaskStates.waiting_for_task_text))
async def process_task_text(message: Message, state: FSMContext):
    """
    Обработчик для получения текста задачи (в состоянии waiting_for_task_text).
    Вызывается после команды /add, когда пользователь отправляет текст задачи.
    Сохраняет текст и просит выбрать категорию.
    """
    task_text = message.text.strip()
    
    # Проверяем, что текст не пустой
    if not task_text:
        await message.answer(
            "❌ Текст задачи не может быть пустым. Попробуйте еще раз:"
        )
        return
    
    # Сохраняем текст задачи во временное хранилище состояния
    await state.update_data(task_text=task_text)
    
    # Переходим к состоянию выбора категории
    await state.set_state(TaskStates.waiting_for_category)
    
    # Отправляем сообщение с кнопками выбора категории
    await message.answer(
        "📝 Текст задачи сохранен!\n"
        "Теперь выберите категорию задачи:",
        reply_markup=get_category_keyboard()
    )


@router.callback_query(StateFilter(TaskStates.waiting_for_category), F.data.startswith("category_"))
async def process_category_selection(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик выбора категории задачи (callback от кнопок категорий).
    Вызывается когда пользователь нажимает кнопку с категорией.
    """
    # Извлекаем категорию из callback_data (format: "category_DataBase")
    category = callback.data.replace("category_", "")
    
    # Получаем сохраненный текст задачи из состояния
    data = await state.get_data()
    task_text = data.get("task_text")
    
    if not task_text:
        # Если текст задачи потерялся, сообщаем об ошибке
        await callback.message.answer("❌ Ошибка: текст задачи не найден. Попробуйте снова с команды /add")
        await state.clear()
        await callback.answer()
        return
    
    # Добавляем задачу в базу данных с выбранной категорией
    task_id = add_task(task_text, callback.from_user.id, category)
    
    # Сбрасываем состояние
    await state.clear()
    
    # Определяем иконку категории для отображения
    category_icons = {
        "DataBase": "💾",
        "Frontend": "🎨",
        "Backend": "⚙️",
        "Business": "💼"
    }
    category_icon = category_icons.get(category, "📋")
    
    # Отправляем подтверждение пользователю
    await callback.message.edit_text(
        f"✅ Задача добавлена!\n\n"
        f"ID: {task_id}\n"
        f"Текст: {task_text}\n"
        f"Категория: {category_icon} {category}"
    )
    
    # Подтверждаем обработку callback
    await callback.answer()


@router.message(StateFilter(TaskStates.waiting_for_task_id))
async def process_task_id(message: Message, state: FSMContext):
    """
    Обработчик для получения ID задачи для удаления (в состоянии waiting_for_task_id).
    Вызывается после команды /delete, когда пользователь отправляет ID задачи.
    """
    try:
        # Пытаемся преобразовать текст в число (ID задачи)
        task_id = int(message.text.strip())
        
        # Пытаемся удалить задачу
        deleted = delete_task(task_id, message.from_user.id)
        
        # Сбрасываем состояние
        await state.clear()
        
        if deleted:
            await message.answer(f"✅ Задача с ID {task_id} успешно удалена!")
        else:
            await message.answer(
                f"❌ Задача с ID {task_id} не найдена или не принадлежит вам."
            )
    except ValueError:
        # Если не удалось преобразовать в число
        await message.answer(
            "❌ ID задачи должен быть числом. Попробуйте еще раз:"
        )


@router.message()
async def handle_other_messages(message: Message, state: FSMContext):
    """
    Обработчик всех остальных сообщений, которые не являются командами.
    Напоминает пользователю о доступных командах.
    Также сбрасывает состояние, если пользователь отправляет что-то неожиданное.
    """
    # Сбрасываем состояние на случай, если пользователь был в процессе добавления/удаления
    await state.clear()
    
    await message.answer(
        "🤔 Я не понимаю эту команду.\n\n"
        "Доступные команды:\n"
        "/start - Начать работу\n"
        "/add - Добавить задачу\n"
        "/delete - Удалить задачу\n"
        "/list - Показать все задачи\n"
        "/list_csv - Экспортировать задачи в CSV"
    )

