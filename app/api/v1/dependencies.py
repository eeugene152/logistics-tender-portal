from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.session import get_async_session
from jose import jwt, JWTError
from app.core.config import settings
from app.crud.user import user_crud


# Указываем, где FastAPI искать токен (в заголовке Authorization)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login/')

# OAuth2 / Bearer Token: Стандарт для мобильных приложений и разделенных (decoupled)
# фронтендов (React/Vue). Токен хранится в localStorage и передается в заголовке.
# Это проще в отладке и не страдает от CSRF-атак.
# Cookies: Стандарт для классических сайтов. Они защищеннее (с флагом HttpOnly), но
# с ними сложнее работать, если фронтенд и бэкенд на разных доменах.
# Мы используем OAuth2, так как FastAPI «из коробки» идеально с ним интегрирован и
# сразу рисует кнопку авторизации в Swagger.


async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(get_async_session)
):
    # 1. Достаем токен из куки
    token = request.cookies.get("users_access_token")
    # 2. Если в куках нет (например, Swagger), проверяем заголовок Authorization
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Токен не найден"
        )

    try:
        # расшифровываем токен
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        # вызов jwt.decode(...). Библиотека python-jose автоматически проверяет
        # поле "exp" (expiration) в токене. Если срок истек, она выбросит
        # исключение JWTError, которое мы перехватываем и превращаем в 401
        # Unauthorized. Руками писать if expire < now не нужно.

        user_id: str = payload.get('sub')
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='ID пользователя не найден'
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Неверный или просроченный токен'
        )

    user = await user_crud.find_one_or_none(session, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Пользователь не найден'
        )

    return user
