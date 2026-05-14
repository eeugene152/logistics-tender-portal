from pydantic import Field, BaseModel, EmailStr, ConfigDict
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
    # Принимаем данные, запрещаем лишнее
    model_config = ConfigDict(extra='forbid')


class SchemaUserCreate(SchemaUserBase):
    hashed_password: str
    # Принимаем данные, запрещаем лишнее
    model_config = ConfigDict(extra='forbid')


class SchemaUserRead(SchemaUserBase):
    id: UUID
    # Читаем из базы, поэтому разрешаем атрибуты
    model_config = ConfigDict(from_attributes=True)
    # Позволяет Pydantic работать с моделями SQLAlchemy
        # нужен только там, где ты возвращаешь данные из базы.


class SchemaUserUpdate(SchemaUserBase):
    email: Optional[EmailStr]
    first_name: Optional[str]
    last_name: Optional[str]
    role: Optional[str]
    phone_num: Optional[str]
    # Принимаем данные, запрещаем лишнее
    model_config = ConfigDict(extra='forbid')


class SchemaUserArchieve(SchemaUserRead):
    archieved: bool
