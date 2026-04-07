import uuid
from datetime import datetime
from typing import Annotated

from pydantic import Field
from sqlalchemy import UUID
from sqlalchemy.orm import (
  DeclarativeBase, Mapped, mapped_column, declared_attr
)
from sqlalchemy.sql import func


str_uniq = Annotated[
    str, Field(max_length=255), mapped_column(unique=True, nullable=False)
]
str_null_true = Annotated[
    str, Field(max_length=255), mapped_column(nullable=True)
]
str_null_false = Annotated[
    str, Field(max_length=255), mapped_column(nullable=False)
]
inn_str = Annotated[str, Field(
    min_length=12, max_length=12
), mapped_column(unique=True, nullable=False)
]
float_two_digits = Annotated[
    float, Field(decimal_places=2), mapped_column(nullable=False)
]


class Base(DeclarativeBase):

    @declared_attr
    def __tablename__(cls):
        return f'{cls.__name__.lower()}s'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    updated_at: Mapped[datetime] = mapped_column(
        #  Даст время при СОЗДАНИИ
        server_default=func.now(),
        # Даст новое время при ОБНОВЕ
        onupdate=func.now()
    )
