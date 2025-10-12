import os
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

load_dotenv(".env.txt")
TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    raise ValueError("❌ TOKEN не найден!")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Глобальный словарь для хранения URL пользователей
user_urls = {} 

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.message.from_user
    
    guide_text = (
        "👋 Привет! Я бот для получения расписания занятий.\n\n"
        "📖 КАК ПОЛУЧИТЬ URL РАСПИСАНИЯ:\n"
        "1. Перейди на сайт: https://lk2.stgau.ru/WebApp/#/Rasp\n"
        "2. Найди свою группу в списке\n"
        "3. Нажми на группу - откроется страница расписания\n"
        "4. Скопируй URL из адресной строки браузера\n"
        "5. Отправь его мне командой: /reg твой_url\n\n"
        "🔗 Пример URL:\n"
        "https://lk2.stgau.ru/WebApp/#/Rasp/Group/22222 \n "
        "По всем вопросам и предложениям писать на ТГ Создателя и владельца бота, он приведен ниже \n"
        " @Pro100_4elovek19"
    )
    
    reply_markup = ReplyKeyboardMarkup([
        ["📋 Зарегистрировать URL"],
        ["📅 Получить расписание", "❓ Помощь"]
    ], resize_keyboard=True)
    
    await update.message.reply_text(
        guide_text,
        reply_markup=reply_markup
    )

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /reg для регистрации URL пользователя"""
    user = update.message.from_user
    user_id = user.id
    
    if not context.args:
        await update.message.reply_text(
            "❌ Использование:\n"
            "/reg ваш_url\n\n"
            "Пример:\n"
            "/reg https://lk2.stgau.ru/WebApp/#/Rasp/Group/22222"
        )
        return
    
    url = ' '.join(context.args)
    
    if not url.startswith('https://lk2.stgau.ru/WebApp/#/Rasp/Group/'):
        await update.message.reply_text(
            "❌ Неверный URL!\n"
            "URL должен начинаться с:\n"
            "https://lk2.stgau.ru/WebApp/#/Rasp/Group/\n\n"
            "Проверь правильность ссылки и попробуй снова."
        )
        return
    
    user_urls[user_id] = url
    group_number = url.split('/')[-1]
    
    await update.message.reply_text(
        f"✅ Регистрация успешна!\n"
        f"Теперь нажми '📅 Получить расписание'!"
    )

async def get_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик получения расписания"""
    user = update.message.from_user
    user_id = user.id
    
    if user_id not in user_urls:
        await update.message.reply_text(
            "❌ Сначала зарегистрируй свой URL!\n"
            "Нажми '📋 Зарегистрировать URL'"
        )
        return
    
    url = user_urls[user_id]
    group_number = url.split('/')[-1]
    
    status_msg = await update.message.reply_text(f"🔄 Получаю расписание")
    
    try:
        # Импортируем функцию парсинга из ParsStgau
        from libs.ParsStgau import parse_schedule_with_containers, send_structured_schedule
        
        schedule_data = await parse_schedule_with_containers(url)
        
        if not schedule_data:
            await status_msg.edit_text("❌ Не удалось получить расписание. Попробуй позже.")
            return
        
        await status_msg.edit_text(f"✅ Найдено {len(schedule_data)} контейнеров с занятиями. Отправляю...")
        
        await send_structured_schedule(update, group_number, schedule_data)
        
    except Exception as e:
        logger.error(f"Ошибка при парсинге: {e}")
        await update.message.reply_text("❌ Ошибка при получении расписания.")

async def handle_register_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки регистрации"""
    await update.message.reply_text(
        "📋 Для регистрации отправь команду:\n"
        "/reg твой_url\n\n"
        "Пример:\n"
        "/reg https://lk2.stgau.ru/WebApp/#/Rasp/Group/22222"
    )

async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды помощи"""
    help_text = (
        "❓ ПОМОЩЬ\n\n"
        "📋 Регистрация:\n"
        "1. Найди URL на сайте расписания\n"
        "2. Отправь: /reg твой_url\n\n"
        "📅 Получить расписание:\n"
        "Нажми кнопку '📅 Получить расписание'\n\n"
        "🔗 Пример URL:\n"
        "https://lk2.stgau.ru/WebApp/#/Rasp/Group/22222\n\n"
        "🔄 Перезапуск: /start"
    )
    await update.message.reply_text(help_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    text = update.message.text
    
    if text == "📋 Зарегистрировать URL":
        await handle_register_button(update, context)
    elif text == "📅 Получить расписание":
        await get_schedule(update, context)
    elif text == "❓ Помощь":
        await handle_help(update, context)
    else:
        await update.message.reply_text("Используй кнопки для навигации 👆")

def setup_handlers(application: Application):
    """Настройка обработчиков для приложения"""
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("reg", register)) 
    application.add_handler(CommandHandler("help", handle_help))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

def create_application():
    """Создание и настройка приложения Telegram"""
    application = Application.builder().token(TOKEN).build()
    setup_handlers(application)
    return application

def run_bot():
    """Запуск бота"""
    application = create_application()
    logger.info("Бот запущен...")
    application.run_polling()
