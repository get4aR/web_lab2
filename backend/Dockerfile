# Образ Python
FROM python:3.12.7
# Рабочая директория
WORKDIR /app
# Копирование requirements.txt
COPY requirements.txt .
# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt
# Копирование остального кода
COPY . .
# Открываем порт 3000
EXPOSE 3000
# Запуск микросервиса
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000"]
