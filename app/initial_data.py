# 3. Создаем скрипт app/initial_data.py:
# Этот скрипт будет импортировать твои Settings, подключаться к базе через SQLAlchemy и делать простую проверку:
# «Есть ли в таблице User запись с email {settings.FIRST_SUPERUSER_EMAIL}?»
# Если нет — создаем запись, ставим флаг is_superuser=True и хешируем пароль.
print("Checking initial data...")