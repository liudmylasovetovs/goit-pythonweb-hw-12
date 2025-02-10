# Використовуємо офіційний Python-образ
FROM python:3.11-slim

# Встановлюємо робочу директорію всередині контейнера
WORKDIR /app

# Оновлюємо pip
RUN pip install --no-cache-dir --upgrade pip

# Копіюємо вручну створений файл requirements.txt (повинен бути у репозиторії)
COPY ./requirements.txt .


# Встановлюємо залежності
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо весь код
COPY . .

# Відкриваємо порт 8000
EXPOSE 8000

# Команда для запуску FastAPI через Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
