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
    && rm -rf /var/lib/apt/lists/*

# Копируем исходники приложения
COPY src/ /app
WORKDIR /app

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем Chromium (без --with-deps!)
RUN playwright install chromium

# Переменные окружения
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Открываем порт (если нужно)
EXPOSE 5000

# Запускаем приложение
CMD ["python", "ParsStgau.py"]
