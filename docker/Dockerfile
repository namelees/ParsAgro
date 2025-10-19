# ===============================
#  Рабочий Dockerfile для Python + Playwright
# ===============================
FROM python:3.11-bookworm

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

COPY src/ ./src/

WORKDIR /src

RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium

# Переменные окружения
ENV PYTHONPATH=/src
ENV PYTHONUNBUFFERED=1

# Указываем рабочую директорию для пользователя
WORKDIR /src

# Команда по умолчанию
CMD ["python", "ParsStgau.py"]
