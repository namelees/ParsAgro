import asyncio
from datetime import datetime
from telegram import Update

async def get_schedule(update: Update, context, user_urls):
    """Получение расписания для пользователя"""
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
    
    print(f"📅 Пользователь {user_id} запросил расписание")
    status_msg = await update.message.reply_text(f"🔄 Получаю расписание...")
    
    try:
        print("🔄 Вызов парсера...")
        await update.message.reply_text("🔍 Запускаю парсер...")
        
        schedule_data = await parse_schedule_with_containers(url)
        
        if not schedule_data:
            await status_msg.edit_text("❌ Не удалось получить расписание. Попробуй позже.")
            return
        
        await status_msg.edit_text(f"✅ Найдено {len(schedule_data)} дней с занятиями. Отправляю...")
        
        await send_structured_schedule(update, group_number, schedule_data)
        
    except Exception as e:
        print(f"Ошибка при парсинге: {e}")
        await update.message.reply_text("❌ Ошибка при получении расписания.")

async def parse_schedule_with_containers(group_url):
    """Парсинг расписания с использованием Playwright"""
    from playwright.async_api import async_playwright
    
    print(f"🔄 ПАРСЕР: Начало для {group_url}")
    
    try:
        print("1. Импорт Playwright...")
        
        async with async_playwright() as p:
            print("2. Запуск браузера...")
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            print("✅ Браузер запущен")
            
            print("3. Создание страницы...")
            page = await browser.new_page()
            print("✅ Страница создана")
            
            # Добавляем обработчик ошибок консоли
            async def handle_console(msg):
                if msg.type in ['error', 'warning']:
                    print(f"🚨 Консоль {msg.type}: {msg.text}")
            
            # Добавляем обработчик ошибок сети
            async def handle_response(response):
                if response.status >= 400:
                    print(f"🚨 HTTP ошибка {response.status}: {response.url}")
            
            page.on("console", handle_console)
            page.on("response", handle_response)
            
            print(f"4. Переход по URL: {group_url}")
            response = await page.goto(group_url, wait_until='networkidle', timeout=60000)
            print(f"✅ Страница загружена. Status: {response.status}")
            
            # Ждем дополнительно для выполнения JavaScript
            print("⏳ Ожидание выполнения JavaScript...")
            try:
                # Пытаемся дождаться появления основного контента
                await page.wait_for_selector('.box-limiter div', timeout=10000)
                print("✅ Основной контент загружен")
            except:
                print("⚠️ Основной контент не найден, ждем 3 секунды...")
                await page.wait_for_timeout(3000)
            
            title = await page.title()
            print(f"✅ Title страницы: {title}")
            
            # Проверяем, есть ли контент на странице
            body_text = await page.text_content('body')
            print(f"📄 Длина контента body: {len(body_text)} символов")
            
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
                    print(f"✅ Контейнер {container_num}: {len(container_data['lessons'])} занятий")
                
                container_num += 1
            
            await browser.close()
            print(f"🎉 ПАРСЕР: Найдено {len(all_containers)} контейнеров")
            return all_containers
            
    except Exception as e:
        print(f"💥 ПАРСЕР: Ошибка: {str(e)}")
        import traceback
        print(f"💥 Traceback: {traceback.format_exc()}")
        return None

async def send_structured_schedule(update: Update, group_name: str, schedule_data: list):
    """Отправка структурированного расписания пользователю"""
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

async def test_playwright(update: Update, context):
    """Тестовая команда для проверки парсера"""
    try:
        print("🧪 ЗАПУСК ТЕСТА PLAYWRIGHT")
        await update.message.reply_text("🧪 Запускаю тест Playwright...")
        
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            print("1. Запуск браузера...")
            await update.message.reply_text("1. 🚀 Запуск браузера...")
            
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            print("✅ Браузер запущен")
            await update.message.reply_text("✅ Браузер запущен")
            
            print("2. Создание страницы...")
            await update.message.reply_text("2. 📄 Создание страницы...")
            page = await browser.new_page()
            print("✅ Страница создана")
            await update.message.reply_text("✅ Страница создана")
            
            print("3. Переход на Google...")
            await update.message.reply_text("3. 🌐 Переход на Google...")
            await page.goto('https://www.google.com', timeout=30000)
            print("✅ Google загружен")
            await update.message.reply_text("✅ Google загружен")
            
            title = await page.title()
            print(f"✅ Title страницы: {title}")
            await update.message.reply_text(f"✅ Title страницы: {title}")
            
            await browser.close()
            print("🎉 ТЕСТ УСПЕШЕН - Playwright работает!")
            await update.message.reply_text("🎉 ТЕСТ УСПЕШЕН! Playwright работает корректно!")
            
    except Exception as e:
        print(f"💥 ТЕСТ ПРОВАЛЕН: {e}")
        await update.message.reply_text(f"❌ ТЕСТ ПРОВАЛЕН: {str(e)}")
