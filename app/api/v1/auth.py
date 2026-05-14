from fastapi import APIRouter, Response, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.session import get_async_session
from app.schemas.auth import SchemaUserAuth, SchemaToken
from app.core.security import authenticate_user, create_access_token
from app.api.v1.dependencies import get_current_user, get_user_by_id_or_404
from app.schemas.auth import (
  SchemaUserRead,
  SchemaUserAuth,
  SchemaUserCreate,
  SchemaUserArchieve,
  SchemaUserRegister,
  SchemaUserUpdate
)
from app.models import User
from app.core.config import settings
from app.crud.user import user_crud
from uuid import UUID


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


@router.get(
    '/list/', response_model=list[SchemaUserArchieve],
    summary='Получить список юзеров'
)
async def get_all_users(
    session: AsyncSession = Depends(get_async_session),
    skip: int = 0,   # Параметр из URL например
    limit: int = 10,  # Параметр из URL например
    order_by: str = "created_at",  # Сортируем по дате создания
    desc: bool = True  # Сначала новые
):
    # чтобы было возможно запрашивать:
    # /users/?skip=10&limit=10 (вторая страница)
    all_users = await user_crud.get_multi(
        session,
        skip=skip,
        limit=limit,
        order_by=order_by,
        desc=desc)
    return all_users


@router.patch(
    '/patch/{user_id}/', response_model=SchemaUserRead,
    response_model_exclude_none=True,
    summary='Изменить данные пользователя'
)
async def update_user(
    obj_in: SchemaUserUpdate,
    user: User = Depends(get_user_by_id_or_404),
    session: AsyncSession = Depends(get_async_session)
):
    updated_user = await user_crud.update(session, db_obj=user, obj_in=obj_in)
    return updated_user


@router.delete(
    '/delete/{user_id}/', response_model=SchemaUserRead,
    response_model_exclude_none=True,
    summary='Полное удаление пользователя'
)
async def hard_delete_user(
    user: User = Depends(get_user_by_id_or_404),
    session: AsyncSession = Depends(get_async_session)
):
    deleted_user = await user_crud.delete(session, db_obj=user)
    return deleted_user


@router.delete(
    '/archieve/{user_id}', response_model=SchemaUserArchieve,
    response_model_exclude_none=True,
    summary='Архивировать пользователя'
)
async def soft_delete_user(
    user: User = Depends(get_user_by_id_or_404),
    session: AsyncSession = Depends(get_async_session)
):
    archieved_user = await user_crud.archieve(session, db_obj=user)
    return archieved_user
