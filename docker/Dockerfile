# Используем официальный Python образ
FROM python:3.11-slim

FROM node:18-bullseye

# Установка системных зависимостей
RUN apt-get update && \
    apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxcb1 \
    libxkbcommon0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Установка Playwright
RUN npx playwright install --with-deps

# Копируем исходный код
COPY src/ /app

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# (Перенесено ниже, чтобы установить браузер от имени пользователя app)

# Создаем директорию для логов
RUN mkdir -p /app/logs

# Устанавливаем переменные окружения
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Указываем рабочую директорию для пользователя
WORKDIR /app

# Устанавливаем только Chromium для Playwright от имени пользователя app,
# чтобы браузеры попали в /home/app/.cache/ms-playwright
RUN playwright install chromium
RUN playwright install-deps

# Открываем порт для health check
EXPOSE 5000

# Команда по умолчанию
CMD ["python", "ParsStgau.py"]
