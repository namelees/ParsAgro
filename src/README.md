# Структура проекта Telegram бота

## Описание
Проект разделен на модули для лучшей организации кода:

### Файлы:
- `main.py` - главный файл для запуска бота
- `libs/telegram.py` - все функции и классы для работы с Telegram API
- `libs/ParsStgau.py` - функции для парсинга расписания с сайта
- `libs/JsonParsStgau.py` - дополнительные функции для работы с JSON

### Запуск:
```bash
python src/main.py
```

### Основные функции в telegram.py:
- `start()` - обработчик команды /start
- `register()` - обработчик команды /reg для регистрации URL
- `get_schedule()` - получение расписания
- `handle_register_button()` - обработчик кнопки регистрации
- `handle_help()` - обработчик помощи
- `handle_message()` - обработчик текстовых сообщений
- `setup_handlers()` - настройка обработчиков
- `create_application()` - создание приложения
- `run_bot()` - запуск бота

### Основные функции в ParsStgau.py:
- `parse_schedule_with_containers()` - парсинг расписания с сайта
- `send_structured_schedule()` - отправка структурированного расписания
