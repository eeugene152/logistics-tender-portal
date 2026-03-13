from __future__ import annotations
# Позволяет писать Mapped[**] без кавычек
# и избыточно не дублировать в back-populates
from typing import TYPE_CHECKING  # Для типизации связей
import uuid
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base, str_null_false

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.trade import Trade


class Location(Base):
    full_address: Mapped[str_null_false]
    short_name: Mapped[str_null_false]
    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('companys.id'), nullable=False
    )
    company: Mapped[Company] = relationship(
        back_populates='locations'
    )
    trades_pickup: Mapped[list[Trade]] = relationship(
        foreign_keys='[Trade.pickup_location_id]',
        back_populates='pickup_location'
    )
    trades_delivery: Mapped[list[Trade]] = relationship(
        foreign_keys='[Trade.delivery_location_id]',
        back_populates='delivery_location'
    )

    @property
    def company_and_address(self) -> str:
        return f'{self.company.company_name}. {self.full_address}'

    def __str__(self) -> str:
        # Технический вывод для разработчика
        return f'{self.full_address} id={self.id}'

    def __repr__(self) -> str:
        # Красивый вывод для человека
        return (f'{self.company.company_name}, '
                f'{self.short_name}, '
                f'{self.full_address}.')
