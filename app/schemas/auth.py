from pydantic import Field, BaseModel, EmailStr
from uuid import UUID
from typing import Optional


class SchemaUserAuth(BaseModel):
    email: EmailStr = Field(..., description='Электронная почта.')
    password: str = Field(
        ..., min_length=5, max_length=50,
        description='Пароль от 5 до 50 знаков.'
    )


class SchemaToken(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Общие поля
class SchemaUserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str]
    last_name: Optional[str]
    role: str
    phone_num: str


# То, что присылает фронтенд при регистрации
class SchemaUserRegister(SchemaUserBase):
    password: str = Field(..., min_length=8)


class SchemaUserCreate(SchemaUserBase):
    hashed_password: str  # = Field(..., min_length=8)


class SchemaUserRead(SchemaUserBase):
    id: UUID

    class Config:
        from_attributes = True # Позволяет Pydantic работать с моделями SQLAlchemy
        # нужен только там, где ты возвращаешь данные из базы.


class SchemaUserUpdate(SchemaUserBase):
    pass
