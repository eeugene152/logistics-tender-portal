from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from app.core.config import settings  # Импортируем напрямую
from jose import jwt
from typing import Optional
from pydantic import EmailStr
from app.crud.user import user_crud
from app.core.hashing import verify_password

# Создаем "контекст" шифрования.
# bcrypt — это стандарт де-факто, надежный и проверенный алгоритм.
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()

    # Если мы передали время при вызове — берем его,
    # если нет — берем стандарт из наших настроек
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({'exp': expire})

    # Кодируем, используя данные напрямую из settings
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


async def authenticate_user(session, email: EmailStr, password: str):
    user = await user_crud.find_one_or_none(session, email=email)
    if not user or verify_password(
        plain_password=password,
        hashed_password=user.hashed_password
    ) is False:
        return None
    return user
