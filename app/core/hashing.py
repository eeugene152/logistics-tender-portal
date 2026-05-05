from passlib.context import CryptContext

# Создаем "контекст" шифрования.
# bcrypt — это стандарт де-факто, надежный и проверенный алгоритм.
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_password_hash(password: str) -> str:
    """
    Превращает чистый пароль в 'абракадабру' (хеш).
    Обратно из хеша достать пароль невозможно.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет, совпадает ли введенный пользователем пароль
    с тем хешем, который лежит у нас в базе.
    """
    return pwd_context.verify(plain_password, hashed_password)
