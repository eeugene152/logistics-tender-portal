from __future__ import annotations
# Позволяет писать Mapped[**] без кавычек
# и избыточно не дублировать в back-populates
from typing import TYPE_CHECKING  # Для типизации связей
import uuid
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base, str_uniq
from app.models.enums import UserType

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.trade import Trade
    from app.models.bid import Bid


class User(Base):
    first_name: Mapped[str]
    last_name: Mapped[str]
    email: Mapped[str_uniq]
    hashed_password: Mapped[str]
    phone_num: Mapped[str_uniq]
    telegram: Mapped[Optional[str]]
    role: Mapped[UserType] = mapped_column(nullable=False)
    # разрешаем None для Админов
    company_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey('companys.id'), nullable=True
    )
    company: Mapped[Company] = relationship(
        back_populates='users'
    )
    trades: Mapped[list[Trade]] = relationship(back_populates='creator')
    bids: Mapped[list[Bid]] = relationship(back_populates='bid_creator')

    @property
    def full_name(self) -> str:
        return f'{self.first_name} {self.last_name}'

    def __str__(self) -> str:
        # Технический вывод для разработчика
        return f'{self.full_name} id={self.id}'

    def __repr__(self) -> str:
        # Красивый вывод для человека
        return (f'{self.full_name}, '
                f'phone_num={self.phone_num}, '
                f'email={self.email}')
