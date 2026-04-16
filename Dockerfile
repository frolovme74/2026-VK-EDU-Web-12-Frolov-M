# Используем Python 3.12 (самый актуальный и стабильный для Django 6)
FROM python:3.12-slim

# Настройки среды
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Устанавливаем минимально необходимые системные пакеты
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Обновляем pip перед установкой зависимостей
RUN pip install --upgrade pip

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем пакеты. Если упадет здесь — мы увидим точную причину.
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальной проект
COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]