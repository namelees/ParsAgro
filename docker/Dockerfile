# ===============================
#  Рабочий Dockerfile для Python + Playwright
# ===============================
FROM python:3.11-slim

# Устанавливаем системные зависимости для Chromium
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
    fonts-liberation \
    fonts-unifont \
    libatk1.0-0 \
    libcups2 \
    libxshmfence1 \
    xdg-utils \
    libnspr4 \     
    libpango-1.0-0 \
    libcairo2 \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем только Chromium для Playwright
RUN playwright install chromium

# Копируем исходный код
COPY src/ ./src/

# Переменные окружения
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Создаем пользователя для безопасности
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Указываем рабочую директорию для пользователя
WORKDIR /app

# Команда по умолчанию
CMD ["python", "src/ParsStgau.py"]
