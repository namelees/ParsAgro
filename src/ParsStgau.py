import os
import asyncio
import logging
import json
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from Infra.groups import load_groups_data, find_group, get_groups_database
from Infra.sheedule import get_schedule, test_playwright

# Загрузка переменных окружения ДО использования
load_dotenv(".env.txt")
TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    raise ValueError("❌ TOKEN не найден!")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

user_urls = {}

# Глобальная переменная для хранения последних логов
bot_logs = []

class TelegramLogHandler(logging.Handler):
    """Кастомный обработчик логов для отправки в Telegram"""
    def __init__(self, bot=None):
        super().__init__()
        self.bot = bot
        self.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    
    def emit(self, record):
        global bot_logs
        log_entry = self.format(record)
        
        # Сохраняем лог в глобальный список
        bot_logs.append(log_entry)
        
        # Ограничиваем размер логов (последние 50 записей)
        if len(bot_logs) > 50:
            bot_logs = bot_logs[-50:]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    
    guide_text = (
        "👋 Привет! Я бот для получения расписания занятий.\n\n"
        "🎯 ДЛЯ НАЧАЛА РАБОТЫ:\n\n"
        "1. Зарегистрируй свою группу:\n"
        "/reg название_группы\n\n"
        "Примеры:\n"
        "/reg ИСП-21-1\n"
        "/reg 22296\n"
        "/reg ПРОГ-20-1\n\n"
        "2. Получай расписание кнопкой ниже!\n\n"
        "📋 Новые команды:\n"
        "/logs - посмотреть логи работы\n"
        "/test - тест парсера\n\n"
        "По всем вопросам: @Pro100_4elovek19"
    )
    
    reply_markup = ReplyKeyboardMarkup([
        ["🎯 Зарегистрировать группу"],
        ["📅 Получить расписание", "❓ Помощь"]
    ], resize_keyboard=True)
    
    await update.message.reply_text(
        guide_text,
        reply_markup=reply_markup
    )

async def show_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать логи бота"""
    user = update.message.from_user
    
    if not bot_logs:
        await update.message.reply_text("📭 Логи пока пусты...")
        return
    
    # Берем последние 20 записей
    recent_logs = bot_logs[-20:]
    logs_text = "📋 **Последние логи бота:**\n\n" + "\n".join(recent_logs)
    
    # Разбиваем на части если слишком длинное сообщение
    if len(logs_text) > 4000:
        logs_text = logs_text[:4000] + "\n\n... (логи обрезаны)"
    
    await update.message.reply_text(f"```\n{logs_text}\n```", parse_mode='MarkdownV2')


async def register_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Регистрация по названию группы"""
    user = update.message.from_user
    user_id = user.id
    
    if not context.args:
        await update.message.reply_text(
            "❌ Использование:\n"
            "/reg название_группы\n\n"
            "Примеры:\n"
            "/reg ИСП-21-1\n"
            "Просто введи номер или название группы!"
        )
        return
    
    group_query = ' '.join(context.args)
    logger.info(f"🔍 Пользователь {user_id} ищет группу: {group_query}")
    
    result = find_group(group_query)
    
    if isinstance(result, list):
        if len(result) == 1:
            group_name, group_url = result[0]
            user_urls[user_id] = group_url
            
            await update.message.reply_text(
                f"✅ Группа зарегистрирована!\n"
                f"📚 Группа: {group_name}\n\n"
                f"Теперь нажми '📅 Получить расписание'!"
            )
            
        elif len(result) > 1:
            keyboard = []
            for group_name, group_url in result[:5]:  
                keyboard.append([f"🎯 {group_name}"])
            
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            
            context.user_data['group_matches'] = result
            
            await update.message.reply_text(
                f"🔍 Найдено {len(result)} групп:\n"
                f"Выбери нужную группу:",
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                f"❌ Группа '{group_query}' не найдена.\n\n"
                f"Попробуй:\n"
                f"• Проверить написание\n"
                f"• Использовать номер группы\n"
                f"• Убедиться, что группа есть в списке"
            )

async def handle_group_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = user.id
    selected_text = update.message.text
    
    if selected_text.startswith("🎯 "):
        selected_group = selected_text[2:] 
    else:
        selected_group = selected_text
    
    matches = context.user_data.get('group_matches', [])
    for group_name, group_url in matches:
        if group_name == selected_group:
            user_urls[user_id] = group_url
            
            reply_markup = ReplyKeyboardMarkup([
                ["🎯 Зарегистрировать группу"],
                ["📅 Получить расписание", "❓ Помощь"]
            ], resize_keyboard=True)
            
            await update.message.reply_text(
                f"✅ Группа {group_name} зарегистрирована!\n\n"
                f"Теперь нажми '📅 Получить расписание'!",
                reply_markup=reply_markup
            )
            
            context.user_data.pop('group_matches', None)
            return
    
    await update.message.reply_text("❌ Ошибка выбора группы")




async def handle_register_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎯 Для регистрации отправь команду:\n"
        "/reg название_группы\n\n"
        "Примеры:\n"
        "/reg 25ИИ-Д-9-2\n"
        "/reg 22296\n"
        "/reg ПРОГ-20-1"
    )

async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "❓ ПОМОЩЬ\n\n"
        "🎯 Регистрация:\n"
        "/reg название_группы\n\n"
        "📅 Получить расписание:\n"
        "Нажми кнопку '📅 Получить расписание'\n\n"
        "🔧 Диагностика:\n"
        "/test - проверить работу парсера\n"
        "/logs - посмотреть логи\n\n"
        "🔄 Перезапуск: /start"
    )
    await update.message.reply_text(help_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text.startswith("🎯 ") or context.user_data.get('group_matches'):
        await handle_group_selection(update, context)
    elif text == "🎯 Зарегистрировать группу":
        await handle_register_button(update, context)
    elif text == "📅 Получить расписание":
        await get_schedule(update, context, user_urls)
    elif text == "❓ Помощь":
        await handle_help(update, context)
    else:
        await update.message.reply_text(
            "Используй кнопки или команды:\n"
            "/reg - регистрация группы\n"
            "/start - инструкция\n"
            "/test - диагностика"
        )

def main():
    load_groups_data()
    
    application = Application.builder().token(TOKEN).build()
    
    # Добавляем кастомный обработчик логов
    telegram_handler = TelegramLogHandler()
    logger.addHandler(telegram_handler)
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("reg", register_group))
    application.add_handler(CommandHandler("help", handle_help))
    application.add_handler(CommandHandler("test", test_playwright))
    application.add_handler(CommandHandler("logs", show_logs))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Бот запущен...")
    
    application.run_polling()

if __name__ == "__main__":
    main()