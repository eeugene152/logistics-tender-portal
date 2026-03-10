#!/bin/sh
set -e # Скрипт упадет, если команда вернет ошибку.

# Проверка критических переменных
if [ -z "$DB_HOST" ] && [ -z "$DB_PORT" ] && [ -z "$POSTGRES_DB" ]; then
  echo "ERROR: Database configuration is missing!"
  exit 1
fi

if [ -z "$SECRET_KEY" ]; then
  echo "WARNING: SECRET_KEY is not set! Auth will not work."
  # Можно либо exit 1, либо просто предупредить
fi


HOST="$DB_HOST"
PORT="$DB_PORT"

# Настройки ожидания
MAX_RETRIES=30
RETRY_COUNT=0
# Ожидание готовности PostgreSQL
echo "Waiting for PostgreSQL at $HOST:$PORT..."
# /dev/null 2>&1: Это просто «затыкание» лишнего вывода команды pg_isready,
# чтобы она не спамила в логи каждые 5 секунд, а мы видели только наши echo
while ! pg_isready -h "$HOST" -p "$PORT" -U "$POSTGRES_USER" > /dev/null 2>&1; do
  RETRY_COUNT=$((RETRY_COUNT + 1))

  if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
    echo "ERROR: PostgreSQL is still unavailable after $MAX_RETRIES seconds. Exiting."
    exit 1
  fi

  echo "PostgreSQL is unavailable (attempt $RETRY_COUNT/$MAX_RETRIES) - sleeping..."
  sleep 1

done
echo "PostgreSQL is UP - proceeding with migrations."

# Применяем миграции
echo "Running migrations..."
if alembic upgrade head; then
  echo "Migrations applied successfully!"
else
  echo "ERROR: Migrations failed to apply! Check your models and database stat."
  echo "Stopping container to prevent data corruption."
  exit 1
fi

# Создаем начальные данные (админа)
echo "if necessary creating initial data..."
python app/initial_data.py

# Запускаем основное приложение (команду, которая была в Dockerfile)
echo "Starting backend..."
# типа я закончил тут - давай дальше что у тебя по списку в докерфайле))
exec "$@"