from fastapi import APIRouter, Response, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.session import get_async_session
from app.schemas.auth import SchemaUserAuth, SchemaToken
from app.core.security import authenticate_user, create_access_token
from app.api.v1.dependencies import get_current_user
from app.schemas.auth import SchemaUserRead, SchemaUserAuth, SchemaUserCreate, SchemaUserRegister
from app.models import User
from app.core.config import settings
from app.crud.user import user_crud


router = APIRouter()


@router.post(
        '/register/', response_model=SchemaUserRead,
        summary='Регистрация пользователя'
    )
async def register_user(
    user_data: SchemaUserRegister,
    session: AsyncSession = Depends(get_async_session)
) -> dict:
    user = await user_crud.find_one_or_none(session, email=user_data.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Пользователь с таким email уже зарегистрирован'
        )
    return await user_crud.create(session, obj_in=user_data)


@router.post(
        '/login/', response_model=SchemaToken,
        summary='Аутентификация пользователя'
    )
async def auth_user(
    response: Response,         # Нужен для установки куки
    user_data: SchemaUserAuth,  # строгая валидация EmailStr
    session: AsyncSession = Depends(get_async_session)
):
    # Теперь email берется из form_data.username (для формы сваггера)
    user = await authenticate_user(
        session,
        email=user_data.email,
        password=user_data.password,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Неверная почта или пароль'
        )
    # 2. Создаем токен
    access_token = create_access_token(data={'sub': str(user.id)})

    # 3. Устанавливаем куку (браузер сохранит её сам)
    response.set_cookie(
        key='users_access_token',  # ищем ключ в респонсе
        value=access_token,        # устанавливаем ему значение сгенеренного токена
        httponly=True,  # запрещает любым скриптам на странице видеть куку
        secure=settings.COOKIE_SECURE,  # Автомат из .env->True только для HTTPS (продакшн)
        samesite='lax',  # защита от атак типа **CSRF**
        max_age=3600    # 1 час
    )
    return {
        'access_token': access_token,
        'token_type': 'bearer'}


@router.post('/logout/', summary='Выход из системы')
async def logout_user(response: Response):
    response.delete_cookie('users_access_token')
    return {'detail': 'Successfully logged out'}


@router.get(
        '/me', response_model=SchemaUserRead,
        summary='Информация о текущем пользователе'
)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
