# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем минимальные системные зависимости для Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    procps \
    libnss3 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libxss1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Копируем исходный код
COPY src/ /app

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем только Chromium для Playwright
RUN playwright install chromium

# Создаем директорию для логов
RUN mkdir -p /app/logs

# Устанавливаем переменные окружения
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Создаем пользователя для безопасности
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Указываем рабочую директорию для пользователя
WORKDIR /app

# Открываем порт для health check
EXPOSE 5000

# Команда по умолчанию
CMD ["python", "ParsStgau.py"]
