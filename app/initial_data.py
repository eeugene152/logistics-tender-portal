# 3. Создаем скрипт app/initial_data.py:
# Этот скрипт будет импортировать твои Settings, подключаться к базе через
# SQLAlchemy и делать простую проверку:
# «Есть ли в таблице User запись с email {settings.FIRST_SUPERUSER_EMAIL}?»
# Если нет — создаем запись, ставим флаг is_superuser=True и хешируем пароль.
import asyncio
from sqlalchemy import select

from app.core.config import settings
from app.core.session import async_session_maker
from app.models.users import User
from app.models.enums import UserType
from app.core.hashing import get_password_hash


async def create_first_superuser():
    """
    Логика создания самого первого пользователя (Админа).
    """
    print('Инициализация: проверка наличия суперпользователя...')

    # 1. Открываем сессию через нашу фабрику
    async with async_session_maker() as session:
        # 2. Ищем пользователя с email из нашего .env
        query = select(User).where(
            User.email == settings.FIRST_SUPERUSER_EMAIL
        )
        result = await session.execute(query)
        user = result.scalar_one_or_none()

        # 3. Если такого пользователя нет — создаем его
        if not user:
            print(
                f'Создаю суперпользователя: {settings.FIRST_SUPERUSER_EMAIL}'
            )

            new_admin = User(
                first_name="Admin",
                last_name="System",
                email=settings.FIRST_SUPERUSER_EMAIL,
                # ВАЖНО: в базу кладем только ХЕШ пароля!
                hashed_password=get_password_hash(
                    settings.FIRST_SUPERUSER_PASSWORD
                ),
                phone_num="0000000000",  # Заглушка для первого входа
                role=UserType.ADMIN,
                # Если у тебя в модели User есть поле is_active
                # или is_superuser — поставь True
            )

            session.add(new_admin)
            await session.commit()
            print("Суперпользователь успешно создан!")
        else:
            print("Суперпользователь уже существует. Пропускаю.")

if __name__ == "__main__":
    # Запускаем асинхронную функцию
    asyncio.run(create_first_superuser())
