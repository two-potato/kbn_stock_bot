FROM python:3.12.3-slim

# Установите зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Скопируйте ваш код в контейнер
COPY bot.py .
COPY parser.py .

# Установите зависимости для Chrome и WebDriver
RUN apt-get update && apt-get install -y \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Установите путь к WebDriver в переменную окружения
ENV PATH="/usr/lib/chromium:/usr/lib/chromium/chromium-driver:${PATH}"

# Запуск приложения
CMD ["python", "bot.py"]