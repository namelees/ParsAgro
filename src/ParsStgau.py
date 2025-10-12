import os
import asyncio
import logging
import threading
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from flask import Flask, jsonify

load_dotenv(".env.txt")  # Убрал .txt
TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    raise ValueError("❌ TOKEN не найден!")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask приложение для health check
app = Flask(__name__)

user_urls = {} 

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        schedule_data = await parse_schedule_with_containers(url)
        
        if not schedule_data:
            await status_msg.edit_text("❌ Не удалось получить расписание. Попробуй позже.")
            return
        
        await status_msg.edit_text(f"✅ Найдено {len(schedule_data)} контейнеров с занятиями. Отправляю...")
        
        await send_structured_schedule(update, group_number, schedule_data)
        
    except Exception as e:
        logger.error(f"Ошибка при парсинге: {e}")
        await update.message.reply_text("❌ Ошибка при получении расписания.")

async def parse_schedule_with_containers(group_url):
    from playwright.async_api import async_playwright
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            await page.goto(group_url, wait_until='networkidle', timeout=30000)
            await page.wait_for_timeout(18000)  
            
            all_containers = []
            container_num = 1
            
            while container_num <= 20:
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
        f"📦 Дней занятий на этой неделе: {len(schedule_data)}\n"
        f"🎯 Занятий: {total_lessons}\n"
        f"🕐 Обновлено: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
        f"Для обновления нажми '📅 Получить расписание'"
    )

async def handle_register_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 Для регистрации отправь команду:\n"
        "/reg твой_url\n\n"
        "Пример:\n"
        "/reg https://lk2.stgau.ru/WebApp/#/Rasp/Group/22222"
    )

async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    text = update.message.text
    
    if text == "📋 Зарегистрировать URL":
        await handle_register_button(update, context)
    elif text == "📅 Получить расписание":
        await get_schedule(update, context)
    elif text == "❓ Помощь":
        await handle_help(update, context)
    else:
        await update.message.reply_text("Используй кнопки для навигации 👆")

# Health check эндпоинт
@app.route('/health')
def health_check():
    """Health check эндпоинт для мониторинга состояния бота"""
    try:
        # Проверяем основные компоненты
        status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "bot_token": "configured" if TOKEN else "missing",
            "registered_users": len(user_urls),
            "version": "1.0.0"
        }
        return jsonify(status), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

def run_flask_app():
    """Запуск Flask приложения в отдельном потоке"""
    app.run(host='0.0.0.0', port=5000, debug=False)

def main():
    # Запускаем Flask в отдельном потоке
    flask_thread = threading.Thread(target=run_flask_app, daemon=True)
    flask_thread.start()
    logger.info("Flask health check сервер запущен на порту 5000")
    
    # Запускаем Telegram бота
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("reg", register)) 
    application.add_handler(CommandHandler("help", handle_help))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Telegram бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()