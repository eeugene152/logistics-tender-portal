from app.models import User
from app.crud.crud_base import CRUDBase
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.auth import (
  SchemaUserRegister,
  SchemaUserUpdate,
  SchemaUserCreate
)
from app.core.hashing import get_password_hash


class CRUDUser(CRUDBase[User, SchemaUserCreate, SchemaUserUpdate]):
    # Переопределяем стандартный метод create
    # т.к. нужно поменять поля с паролями (обычный-хешированный)
    async def create(
        self, session: AsyncSession, *, obj_in: SchemaUserRegister
    ):
        # Превращаем схему регистрации в словарь
        obj_in_data = obj_in.model_dump()
        # Вырезаем "голый" пароль
        password = obj_in_data.pop('password')
        # Хешируем и добавляем в словарь уже нужное поле для модели
        obj_in_data['hashed_password'] = get_password_hash(password=password)
        updated_obj_in = SchemaUserCreate(**obj_in_data)
        # передаем обработанные данные с хешем в нужной схеме
        # родителю и задействуем остальной стандартный код функции create.
        return await super().create(session, obj_in=updated_obj_in)


user_crud = CRUDUser(User)
