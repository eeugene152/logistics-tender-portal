from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import TypeVar, Generic, Type, Optional, Any, List
from pydantic import BaseModel


# Объявляем переменные для типов, чтобы CRUD понимал, с какой моделью и схемой работает
ModelType = TypeVar('ModelType')
CreateSchematype = TypeVar('CreateSchemaType', bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchematype]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(
        self, session: AsyncSession, obj_id: Any
    ) -> Optional[ModelType]:
        query = select(self.model).where(self.model.id == obj_id)
        result = await session.execute(query)
        return result.scalars().first()

    async def get_multi(
        self, session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        query = select(self.model).offset(skip).limit(limit)
        result = await session.execute(query)
        return result.scalars().all()

    async def create(
        self, session: AsyncSession, *, obj_in: CreateSchematype
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