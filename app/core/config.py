import os

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL

ROOT_DIR_ENV = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", ".env"
)


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    FIRST_SUPERUSER_EMAIL: str
    FIRST_SUPERUSER_PASSWORD: str

    model_config = SettingsConfigDict(
        env_file=ROOT_DIR_ENV,
        env_file_encoding='utf-8',
        extra="ignore" # Игнорировать лишние переменные в .env
    )

    @property
    def DATABASE_URL(self) -> str:
        # Собираем URL через SQLAlchemy, используя self
        url_obj = URL.create(
            drivername="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            database=self.POSTGRES_DB,
        )
        # Возвращаем строку, а не объект, т.к.
        # app/alembic/env.py ждет именно строку
        # hide_password=False важен, иначе пароль заменится на ***
        return url_obj.render_as_string(hide_password=False)


# Создаем экземпляр, который будем импортировать в другие файлы
settings = Settings()
