from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import TypeVar, Generic, Type, Optional, Any, List, Union
from pydantic import BaseModel


# Объявляем переменные для типов, чтобы CRUD понимал, с какой
# моделью и схемой работает
ModelType = TypeVar('ModelType')
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(
        self, session: AsyncSession, obj_id: Any
    ) -> Optional[ModelType]:
        query = select(self.model).where(self.model.id == obj_id)
        result = await session.execute(query)
        return result.scalars().first()

    async def get_multi(
        self,
        session: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        # По какому полю (по умолчанию created_at)
        order_by: Optional[str] = "created_at",
        # В какую сторону (по умолчанию по возрастанию)
        desc: bool = False
    ) -> List[ModelType]:
        # 1. Берем поле из модели для определения сортировки
        column = getattr(self.model, order_by, self.model.id)
        # 2. Определяем направление (asc - по возр., desc - по убыв.)
        if desc:
            column = column.desc()

        query = select(self.model).offset(skip).limit(limit).order_by(column)
        result = await session.execute(query)
        return result.scalars().all()

    async def create(
        self, session: AsyncSession, *, obj_in: CreateSchemaType
    ) -> ModelType:
        # Превращаем Pydantic-схему в словарь
        obj_in_data = obj_in.model_dump()
        # Создаем объект модели
        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def find_one_or_none(
        self, session: AsyncSession, **filter_by
    ) -> Optional[ModelType]:
        query = select(self.model).filter_by(**filter_by)
        result = await session.execute(query)
        return result.scalars().first()

    async def update(
            self,
            session: AsyncSession,
            *,
            # Живой объект из базы (например, User)
            db_obj: ModelType,
            # Схема обновления (UserUpdate) ИЛИ обычный словарь
            obj_in: Union[UpdateSchemaType, dict]
    ) -> ModelType:  # Метод возвращает обновленную модель
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(
                exclude_unset=True, exclude_none=True
            )
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    # hard delete
    async def delete(self, session: AsyncSession, *, db_obj: ModelType):
        await session.delete(db_obj)
        await session.commit()
        return db_obj

    # soft delete
    async def archieve(self, session: AsyncSession, *, db_obj: ModelType):
        if hasattr(db_obj, 'archieved'):
            setattr(db_obj, 'archieved', True)
            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
            return db_obj
