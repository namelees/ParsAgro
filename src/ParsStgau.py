
import os
import asyncio
import logging
import json
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from pathlib import Path

def load_groups_data():
    # Всегда используйте __file__ для определения пути
    base_dir = Path(__file__).parent
    json_path = base_dir / 'groups_data.json'
    
    print(f"🔄 Попытка загрузить: {json_path}")
    
    if not json_path.exists():
        print(f"❌ Файл не найден! Доступные файлы:")
        for f in base_dir.iterdir():
            print(f"   - {f.name}")
        return None
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ JSON загружен успешно, элементов: {len(data) if isinstance(data, dict) else 'N/A'}")
        return data
    except Exception as e:
        print(f"❌ Ошибка загрузки: {e}")
        return None

# Использование
groups_data = load_groups_data()

load_dotenv(".env.txt")
TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    raise ValueError("❌ TOKEN не найден!")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

user_urls = {} 
groups_database = {}

def load_groups_data():
    """Загружает данные групп из файла (синхронная версия)"""
    global groups_database
    try:
        with open('groups_data.json', 'r', encoding='utf-8') as f:
            groups_database = json.load(f)
        logger.info(f"✅ Загружено {len(groups_database)} групп из файла")
    except FileNotFoundError:
        logger.error("❌ Файл groups_data.json не найден")
        groups_database = {}
    except Exception as e:
        logger.error(f"❌ Ошибка загрузки групп: {e}")
        groups_database = {}

def find_group(query):
    """Умный поиск группы по названию или номеру"""
    query = query.strip().lower()
    
    for group_name, group_url in groups_database.items():
        if group_name.lower() == query:
            return group_name, group_url
    
    if query.isdigit():
        for group_name, group_url in groups_database.items():
            if query in group_url:
                return group_name, group_url
    matches = []
    for group_name, group_url in groups_database.items():
        if query in group_name.lower():
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
            "/reg 22296\n"
            "/reg ПРОГ-20-1\n\n"
            "Просто введи номер или название группы!"
        )
        return
    
    group_query = ' '.join(context.args)
    
    result = find_group(group_query)
    
    if isinstance(result, tuple):
        group_name, group_url = result
        user_urls[user_id] = group_url
        
        await update.message.reply_text(
            f"✅ Группа зарегистрирована!\n"
            f"📚 Группа: {group_name}\n\n"
            f"Теперь нажми '📅 Получить расписание'!"
        )
        
    elif isinstance(result, list) and len(result) > 0:
        if len(result) == 1:
            group_name, group_url = result[0]
            user_urls[user_id] = group_url
            await update.message.reply_text(f"✅ Группа {group_name} зарегистрирована!")
        else:
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
    """Обработка выбора группы из предложенных вариантов"""
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
    
    status_msg = await update.message.reply_text(f"🔄 Получаю расписание...")
    
    try:
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
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            await page.goto(group_url, wait_until='networkidle', timeout=30000)
            await page.wait_for_timeout(18000)  
            
            all_containers = []
            container_num = 1
            
            while container_num <= 50:
                container_selector = f'#page-main > div > div > div:nth-child(7) > div > div > div:nth-child({container_num}) > div > div'
                container = await page.query_selector(container_selector)
                
                if not container:
                    logger.info(f"Контейнер {container_num} не найден, завершаем")
                    break
                
                await container.scroll_into_view_if_needed()
                await page.wait_for_timeout(500)
                
                container_data = {
                    'container_number': container_num,
                    'lessons': []
                }
                
                lesson_num = 1
                while lesson_num <= 50:
                    lesson_selector = f'{container_selector} > div:nth-child({lesson_num})'
                    lesson_element = await page.query_selector(lesson_selector)
                    
                    if not lesson_element:
                        break
                    
                    await lesson_element.scroll_into_view_if_needed()
                    await page.wait_for_timeout(200)
                    
                    text = await lesson_element.text_content()
                    if text and text.strip():
                        container_data['lessons'].append({
                            'lesson_number': lesson_num,
                            'text': text.strip()
                        })
                        logger.info(f"Найдено занятие {lesson_num} в контейнере {container_num}")
                    
                    lesson_num += 1
                
                if container_data['lessons']:
                    all_containers.append(container_data)
                    logger.info(f"Контейнер {container_num} содержит {len(container_data['lessons'])} занятий")
                
                container_num += 1
            
            await browser.close()
            logger.info(f"Всего найдено контейнеров: {len(all_containers)}")
            return all_containers
            
        except Exception as e:
            await browser.close()
            logger.error(f"Ошибка при парсинге: {e}")
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
        "/reg ПРОГ-20-1\n\n"
        "Просто введи номер или название группы!\n"
        "стоит отметить, что некоторые группы пишутся с использованием и верхнего и нижнего регистра"
    )

async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "❓ ПОМОЩЬ\n\n"
        "🎯 Регистрация:\n"
        "/reg название_группы\n\n"
        "Примеры:\n"
        "/reg 25ИИ-Д-9-2\n"
        "/reg 22296\n"
        "/reg ПРОГ-20-1\n\n"
        "📅 Получить расписание:\n"
        "Нажми кнопку '📅 Получить расписание'\n\n"
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
            "/start - инструкция"
        )

def main():
    """Основная функция запуска бота"""
    load_groups_data()
    
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("reg", register_group))
    application.add_handler(CommandHandler("help", handle_help))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Бот запущен...")
    
    application.run_polling()

if __name__ == "__main__":
    main()