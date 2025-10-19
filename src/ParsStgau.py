import os
import asyncio
import logging
import json
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Загрузка переменных окружения ДО использования
load_dotenv(".env.txt")
TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    raise ValueError("❌ TOKEN не найден!")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

user_urls = {} 
groups_database = {}

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

def load_groups_data():
    """Загружает данные групп из файла"""
    global groups_database
    possible_paths = [
        'src/groups_data.json',
        './src/groups_data.json', 
        f'{os.getcwd()}/src/groups_data.json',
        'groups_data.json',
        os.path.join(os.path.dirname(__file__), 'groups_data.json'),
    ]
    
    for file_path in possible_paths:
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    groups_database = json.load(f)
                logger.info(f"✅ Загружено {len(groups_database)} групп из {file_path}")
                return
        except Exception as e:
            logger.warning(f"⚠️ Не удалось загрузить из {file_path}: {e}")
            continue
    
    logger.error("❌ Файл groups_data.json не найден ни по одному пути!")
    groups_database = {}

def find_group(query):
    """Умный поиск группы по названию или номеру"""
    query = query.strip()
    
    # 1. Точное совпадение (с учетом регистра)
    if query in groups_database:
        return [(query, groups_database[query])]
    
    # 2. Поиск по номеру группы в URL
    if query.isdigit():
        matches = []
        for group_name, group_url in groups_database.items():
            if query in group_url:
                matches.append((group_name, group_url))
        if matches:
            return matches
    
    # 3. Поиск по частичному совпадению
    matches = []
    for group_name, group_url in groups_database.items():
        if query in group_name:
            matches.append((group_name, group_url))
        elif query.lower() in group_name.lower():
            matches.append((group_name, group_url))
    
    return matches

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

async def test_playwright(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Тестовая команда для проверки парсера"""
    try:
        logger.info("🧪 ЗАПУСК ТЕСТА PLAYWRIGHT")
        await update.message.reply_text("🧪 Запускаю тест Playwright...")
        
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            logger.info("1. Запуск браузера...")
            await update.message.reply_text("1. 🚀 Запуск браузера...")
            
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            logger.info("✅ Браузер запущен")
            await update.message.reply_text("✅ Браузер запущен")
            
            logger.info("2. Создание страницы...")
            await update.message.reply_text("2. 📄 Создание страницы...")
            page = await browser.new_page()
            logger.info("✅ Страница создана")
            await update.message.reply_text("✅ Страница создана")
            
            logger.info("3. Переход на Google...")
            await update.message.reply_text("3. 🌐 Переход на Google...")
            await page.goto('https://www.google.com', timeout=30000)
            logger.info("✅ Google загружен")
            await update.message.reply_text("✅ Google загружен")
            
            title = await page.title()
            logger.info(f"✅ Title страницы: {title}")
            await update.message.reply_text(f"✅ Title страницы: {title}")
            
            await browser.close()
            logger.info("🎉 ТЕСТ УСПЕШЕН - Playwright работает!")
            await update.message.reply_text("🎉 ТЕСТ УСПЕШЕН! Playwright работает корректно!")
            
    except Exception as e:
        logger.error(f"💥 ТЕСТ ПРОВАЛЕН: {e}")
        await update.message.reply_text(f"❌ ТЕСТ ПРОВАЛЕН: {str(e)}")

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

async def get_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = user.id
    
    if user_id not in user_urls:
        await update.message.reply_text(
            "❌ Сначала зарегистрируй свою группу!\n"
            "Нажми '🎯 Зарегистрировать группу'"
        )
        return
    
    url = user_urls[user_id]
    group_number = url.split('/')[-1]
    
    logger.info(f"📅 Пользователь {user_id} запросил расписание")
    status_msg = await update.message.reply_text(f"🔄 Получаю расписание...")
    
    try:
        logger.info("🔄 Вызов парсера...")
        await update.message.reply_text("🔍 Запускаю парсер...")
        
        schedule_data = await parse_schedule_with_containers(url)
        
        if not schedule_data:
            await status_msg.edit_text("❌ Не удалось получить расписание. Попробуй позже.")
            return
        
        await status_msg.edit_text(f"✅ Найдено {len(schedule_data)} дней с занятиями. Отправляю...")
        
        await send_structured_schedule(update, group_number, schedule_data)
        
    except Exception as e:
        logger.error(f"Ошибка при парсинге: {e}")
        await update.message.reply_text("❌ Ошибка при получении расписания.")

async def parse_schedule_with_containers(group_url):
    from playwright.async_api import async_playwright
    
    logger.info(f"🔄 ПАРСЕР: Начало для {group_url}")
    
    try:
        logger.info("1. Импорт Playwright...")
        
        async with async_playwright() as p:
            logger.info("2. Запуск браузера...")
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            logger.info("✅ Браузер запущен")
            
            logger.info("3. Создание страницы...")
            page = await browser.new_page()
            logger.info("✅ Страница создана")
            
            logger.info(f"4. Переход по URL: {group_url}")
            response = await page.goto(group_url, wait_until='networkidle', timeout=60000)
            logger.info(f"✅ Страница загружена. Status: {response.status}")
            
            title = await page.title()
            logger.info(f"✅ Title страницы: {title}")
            
            # Упрощенный парсинг для теста
            all_containers = []
            container_num = 1
            
            while container_num <= 10:  # Ограничим для теста
                container_selector = f'#page-main > div > div > div:nth-child(7) > div > div > div:nth-child({container_num}) > div > div'
                container = await page.query_selector(container_selector)
                
                if not container:
                    break
                
                container_data = {
                    'container_number': container_num,
                    'lessons': []
                }
                
                lesson_num = 1
                while lesson_num <= 10:
                    lesson_selector = f'{container_selector} > div:nth-child({lesson_num})'
                    lesson_element = await page.query_selector(lesson_selector)
                    
                    if not lesson_element:
                        break
                    
                    text = await lesson_element.text_content()
                    if text and text.strip():
                        container_data['lessons'].append({
                            'lesson_number': lesson_num,
                            'text': text.strip()
                        })
                    
                    lesson_num += 1
                
                if container_data['lessons']:
                    all_containers.append(container_data)
                    logger.info(f"✅ Контейнер {container_num}: {len(container_data['lessons'])} занятий")
                
                container_num += 1
            
            await browser.close()
            logger.info(f"🎉 ПАРСЕР: Найдено {len(all_containers)} контейнеров")
            return all_containers
            
    except Exception as e:
        logger.error(f"💥 ПАРСЕР: Ошибка: {str(e)}")
        import traceback
        logger.error(f"💥 Traceback: {traceback.format_exc()}")
        return None

async def send_structured_schedule(update: Update, group_name: str, schedule_data: list):
    total_lessons = sum(len(container['lessons']) for container in schedule_data)
    
    for container in schedule_data:
        Day_num = container['container_number']
        lessons = container['lessons']
        
        if not lessons:
            continue
        
        container_header = (
            f"📦 ДЕНЬ #{Day_num}\n"
            f"📚 Занятий: {len(lessons)}\n"
        )
        await update.message.reply_text(container_header)
        
        for lesson in lessons:
            lesson_num = lesson['lesson_number']
            lesson_text = lesson['text']
            
            lesson_message = (
                f"🎯 Занятие {lesson_num}\n"
                f"{'─'*20}\n"
                f"{lesson_text}\n"
                f"{'─'*20}"
            )
            
            await update.message.reply_text(lesson_message)
            await asyncio.sleep(0.2)
        
        await asyncio.sleep(0.3)
    
    await update.message.reply_text(
        f"✅ Расписание полностью загружено!\n"
        f"📦 Дней занятий: {len(schedule_data)}\n"
        f"🎯 Всего занятий: {total_lessons}\n"
        f"🕐 Обновлено: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
        f"Для обновления нажми '📅 Получить расписание'"
    )

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
        await get_schedule(update, context)
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