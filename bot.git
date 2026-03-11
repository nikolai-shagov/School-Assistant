import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import json
from pathlib import Path

WAITING_FOR_DATE = 1
CORRECT = 2
WRONG = 3

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
    """Загрузить данные пользователя из файла"""
    if Path(DATA_FILE).exists():
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_user_data(data):
    """Сохранить данные пользователя в файл"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    user_id = str(update.effective_user.id)
    user_data = load_user_data()
    
    if user_id not in user_data:
        user_data[user_id] = {
            "user_id": user_id,
            "username": update.effective_user.username or "Неизвестный пользователь",
            "win_streak": 0,
            "total_correct": 0,
            "total_answered": 0
        }
        save_user_data(user_data)
    
    await update.message.reply_text(
        f"Привет {update.effective_user.first_name}! 👋\n\n"
        f"Я бот для изучения исторических дат.\n"
        f"Я напишу событие, а ты напишешь дату.\n\n"
        f"Твои статистика:\n"
        f"🔥 Текущая серия побед: {user_data[user_id]['win_streak']}\n"
        f"✅ Правильных ответов: {user_data[user_id]['total_correct']}\n"
        f"📝 Всего ответов: {user_data[user_id]['total_answered']}\n\n"
        f"Команды:\n"
        f"/start - начать заново\n"
        f"/stats - посмотреть статистику\n"
        f"/next - следующий вопрос\n"
        f"/help - помощь\n\n"
        f"Напиши /next чтобы начать!"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help"""
    await update.message.reply_text(
        "📚 Правила игры:\n\n"
        "1. Я напишу исторический событие\n"
        "2. Ты должен написать год, когда оно произошло\n"
        "3. Если ответ правильный, твоя серия побед +1\n"
        "4. Если ошибка, серия побед обнулится\n\n"
        "Команды:\n"
        "/next - следующий вопрос\n"
        "/stats - твоя статистика\n"
        "/start - начать заново\n"
        "/help - эта справка"
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /stats"""
    user_id = str(update.effective_user.id)
    user_data = load_user_data()
    
    if user_id not in user_data:
        await update.message.reply_text("Ты еще не начал играть. Напиши /start")
        return
    
    user = user_data[user_id]
    accuracy = 0
    if user['total_answered'] > 0:
        accuracy = (user['total_correct'] / user['total_answered']) * 100
    
    await update.message.reply_text(
        f"📊 Твоя статистика:\n\n"
        f"🆔 ID: {user_id}\n"
        f"👤 Юзернейм: {user['username']}\n"
        f"🔥 Текущая серия побед: {user['win_streak']}\n"
        f"✅ Правильных ответов: {user['total_correct']}\n"
        f"📝 Всего ответов: {user['total_answered']}\n"
        f"🎯 Точность: {accuracy:.1f}%"
    )

async def next_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /next или начало беседы"""
    user_id = str(update.effective_user.id)
    user_data = load_user_data()
    
    if user_id not in user_data:
        user_data[user_id] = {
            "user_id": user_id,
            "username": update.effective_user.username or "Неизвестный пользователь",
            "win_streak": 0,
            "total_correct": 0,
            "total_answered": 0
        }
    
    import random
    event = random.choice(HISTORICAL_EVENTS)
    context.user_data['current_event'] = event
    
    await update.message.reply_text(
        f"📖 Какой год? 🤔\n\n{event['event']}"
    )
    
    return WAITING_FOR_DATE

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка ответа пользователя"""
    user_id = str(update.effective_user.id)
    user_data = load_user_data()
    
    if user_id not in user_data:
        await update.message.reply_text("Пожалуйста, напиши /start")
        return WAITING_FOR_DATE
    
    try:
        user_answer = int(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("❌ Пожалуйста, напиши только число (год)")
        return WAITING_FOR_DATE
    
    event = context.user_data.get('current_event')
    if not event:
        await update.message.reply_text("Ошибка. Напиши /next")
        return WAITING_FOR_DATE
    
    correct_year = event['date']
    user_data[user_id]['total_answered'] += 1
    
    if user_answer == correct_year:
        user_data[user_id]['win_streak'] += 1
        user_data[user_id]['total_correct'] += 1
        save_user_data(user_data)
        
        await update.message.reply_text(
            f"✅ Правильно! Это был {correct_year} год!\n\n"
            f"🔥 Серия побед: {user_data[user_id]['win_streak']}\n"
            f"✅ Всего правильных: {user_data[user_id]['total_correct']}\n\n"
            f"Напиши /next для следующего вопроса"
        )
    else:
        user_data[user_id]['win_streak'] = 0
        save_user_data(user_data)
        
        await update.message.reply_text(
            f"❌ Неправильно! Это был {correct_year} год.\n"
            f"📖 События: {event['event']}\n\n"
            f"🔥 Твоя серия побед обнулена\n\n"
            f"Напиши /next для следующего вопроса"
        )
    
    return WAITING_FOR_DATE

def main():
    """Основная функция"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("ERROR: TELEGRAM_BOT_TOKEN не установлен в переменных окружения!")
        return
    
    application = Application.builder().token(token).build()
    
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("next", next_question),
            MessageHandler(filters.TEXT & ~filters.COMMAND, next_question)
        ],
        states={
            WAITING_FOR_DATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)
            ]
        },
        fallbacks=[
            CommandHandler("next", next_question),
            CommandHandler("stats", stats),
            CommandHandler("help", help_command),
            CommandHandler("start", start)
        ]
    )
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("next", next_question))
    application.add_handler(conv_handler)
    
    print("🤖 Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()
