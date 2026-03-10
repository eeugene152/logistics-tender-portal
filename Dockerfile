# образ на основе базового слоя - файлы ОС и интерпретатор python:3.13
FROM python:3.12-slim
# Т.к. у нас python-slim, ставим системные зависимости для работы с Postgres
# (чтобы отработал entrypoint - проверка готовности базы (pg_isready))
# Устанавливаем зависимости для сборки (gcc и библиотеки для Postgres)
# Мы ставим их, а в конце удаляем мусор, чтобы образ остался маленьким
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*
# переход в директорию проекта в образе
WORKDIR /app
# gunicorn уже поставили. так что шаг пропускаем
# копируем с лок компа файл с зависимостями "." - текущий каталог
COPY requirements.txt .
# запускаем его, устанавливаем зависимости
RUN pip install -r requirements.txt --no-cache-dir
# отправка логов в консоль Docker сразу без накопления
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# Скопировать всё содержимое в текущую папку
COPY . .
# скрипт подготовительные действия внутри контейнера перед тем, как запустится само приложение
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
# команда запуска проекта
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "main:app", "-b", "0.0.0.0:8000", "--log-level", "info"]