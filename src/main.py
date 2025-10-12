#!/usr/bin/env python3
"""
Главный файл для запуска Telegram бота расписания
"""

import logging
from libs.telegram import run_bot

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Главная функция для запуска бота"""
    try:
        logger.info("Запуск Telegram бота...")
        run_bot()
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        raise

if __name__ == "__main__":
    main()
