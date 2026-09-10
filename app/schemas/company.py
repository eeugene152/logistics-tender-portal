from pydantic import (
  BaseModel,
  ConfigDict,
  Field,
  field_validator,
  BeforeValidator
)
from typing import Annotated, Any
from uuid import UUID
from app.models.enums import CompanyType


# Функция, которая сработает ДО основной валидации Pydantic.
# Она принудительно превращает числа из Excel в обычный текст.
def cast_to_string(value: Any) -> str:
    if value is None:
        return ''
    # Если прилетело число (например, 7736207543), делаем из него строку
    # Если прилетел float (иногда Excel делает 7736207543.0), отрезаем точку
    if isinstance(value, float):
        return str(int(value)).strip()
    return str(value).strip()


class SchemaCompanyBase(BaseModel):
    company_name: str = Field(..., description='Название компании')
    # company_inn: str = Field(..., description='ИНН компании')

    # Оборачиваем поле company_inn в BeforeValidator.
    # Теперь сюда можно скармливать и числа, и строки — всё станет строкой!
    company_inn: Annotated[
        str, BeforeValidator(cast_to_string)
    ] = Field(..., description="ИНН компании")

    @field_validator('company_inn', check_fields=False)
    @classmethod
    def validate_inn(cls, value: str) -> str:
        # Здесь value УЖЕ гарантированно является чистой
        # строкой благодаря cast_to_string!
        if not value.isdigit():
            raise ValueError("ИНН должен состоять только из цифр")
        if len(value) not in (10, 12):
            raise ValueError(
                "ИНН юридического лица должен быть 10 цифр, а ИП — 12 цифр"
            )
        return value


class SchemaCompanyCreate(SchemaCompanyBase):
    # Если этих колонок не будет в Excel/JSON, Pydantic подставит их сам:
    company_type: CompanyType = CompanyType.CUSTOMER
    is_active: bool = True

    # Защита от мусора и опечаток фронтендеров / админов
    model_config = ConfigDict(extra='forbid')


class SchemaCompanyRead(SchemaCompanyBase):
    id: UUID
    archived: bool

    model_config = ConfigDict(from_attributes=True)
