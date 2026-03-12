import os
import json
import random
from pathlib import Path
from telegram import Update
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    filters, 
    ContextTypes, 
    ConversationHandler
)

# Состояния беседы
WAITING_FOR_DATE = 1

HISTORICAL_EVENTS = [
    {"event": "Падение Римской империи", "date": 476},
    {"event": "Начало Средних веков", "date": 500},
    {"event": "Крещение Руси", "date": 988},
    {"event": "Великая Французская революция", "date": 1789},
    {"event": "Американская революция", "date": 1776},
    {"event": "Войсковая Октябрьская революция в России", "date": 1917},
    {"event": "Начало Первой мировой войны", "date": 1914},
    {"event": "Конец Второй мировой войны в Европе", "date": 1945},
    {"event": "Полёт Юрия Гагарина в космос", "date": 1961},
    {"event": "Падение Берлинской стены", "date": 1989},
    {"event": "Распад Советского союза", "date": 1991},
    {"event": "Стивен Хокинг рождение", "date": 1942},
    {"event": "Изобретение интернета", "date": 1969},
    {"event": "Первая Олимпиада в Древней Греции", "date": 776},
    {"event": "Завоевание Константинополя", "date": 1453},
]

DATA_FILE = "user_data.json"

def load_user_data():
    if Path(DATA_FILE).exists():
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_user_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_data = load_user_data()
    
    if user_id not in user_data:
        user_data[user_id] = {
            "username": update.effective_user.username or "Anonymous",
            "win_streak": 0,
            "total_correct": 0,
            "total_answered": 0
        }
        save_user_data(user_data)
    
    user = user_data[user_id]
    await update.message.reply_text(
        f"Привет, {update.effective_user.first_name}! 👋\n"
        f"Статистика:\n🔥 Серия: {user['win_streak']}\n✅ Правильно: {user['total_correct']}\n"
        f"Напиши /next, чтобы начать!"
    )
    return ConversationHandler.END # Сбрасываем состояние, если нажали старт

async def next_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    event = random.choice(HISTORICAL_EVENTS)
    context.user_data['current_event'] = event
    
    await update.message.reply_text(f"📖 Какой год?\n\n<b>{event['event']}</b>", parse_mode="HTML")
    return WAITING_FOR_DATE

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_data = load_user_data()
    
    # Проверка на наличие данных (на случай, если файл удалили во время игры)
    if user_id not in user_data:
        user_data[user_id] = {"username": "User", "win_streak": 0, "total_correct": 0, "total_answered": 0}

    text = update.message.text.strip()
    if not text.isdigit():
        await update.message.reply_text("❌ Пожалуйста, введи только число (год).")
        return WAITING_FOR_DATE

    user_answer = int(text)
    event = context.user_data.get('current_event')
    
    if not event:
        await update.message.reply_text("Нажми /next для начала.")
        return ConversationHandler.END

    correct_year = event['date']
    user_data[user_id]['total_answered'] += 1
    
    if user_answer == correct_year:
        user_data[user_id]['win_streak'] += 1
        user_data[user_id]['total_correct'] += 1
        msg = f"✅ Верно! Это {correct_year} год.\n🔥 Серия: {user_data[user_id]['win_streak']}"
    else:
        user_data[user_id]['win_streak'] = 0
        msg = f"❌ Ошибка! Это был {correct_year} год.\nСерия обнулена."

    save_user_data(user_data)
    await update.message.reply_text(msg + "\n\nЖми /next для следующего вопроса.")
    return ConversationHandler.END # Завершаем шаг, чтобы ждать /next

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_data = load_user_data()
    user = user_data.get(user_id)
    
    if not user:
        await update.message.reply_text("Сначала поиграй! /next")
        return

    acc = (user['total_correct'] / user['total_answered'] * 100) if user['total_answered'] > 0 else 0
    await update.message.reply_text(f"📊 Статистика:\nСерия: {user['win_streak']}\nТочность: {acc:.1f}%")

def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("Ошибка: Нет токена!")
        return

    application = Application.builder().token(token).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("next", next_question)],
        states={
            WAITING_FOR_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)]
        },
        fallbacks=[CommandHandler("start", start)],
        allow_reentry=True
    )

    # Важен порядок добавления!
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stats", stats))

    print("Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()
