from __future__ import annotations
# Позволяет писать Mapped[**] без кавычек
# и избыточно не дублировать в back-populates
from typing import TYPE_CHECKING  # Для типизации связей

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base, inn_str, str_uniq
from app.models.enums import CompanyType


# Вот она, магия! Этот импорт сработает ТОЛЬКО для IDE
if TYPE_CHECKING:
    from app.models.users import User
    from app.models.location import Location
    from app.models.trade import Trade
    from app.models.bid import Bid
    from app.models.driver import Driver
    from app.models.vehicle import Vehicle


class Company(Base):
    company_name: Mapped[str_uniq]
    company_inn: Mapped[inn_str]
    # Для Enum указываем тип и дефолтное значение
    company_type: Mapped[CompanyType] = mapped_column(
        default=CompanyType.CUSTOMER
    )
    is_active: Mapped[bool] = mapped_column(default=True)

    # Определяем отношения: одна компания может иметь много сотрудников
    # В relationship используем СТРОКУ 'User'
    # (SQLAlchemy сама найдет класс в реестре)
    users: Mapped[list[User]] = relationship(
        back_populates='company', cascade='all, delete-orphan'
    )
    locations: Mapped[list[Location]] = relationship(
        back_populates='company',
        cascade='all, delete-orphan'  # Если удалим компанию - удалим и локацию
    )
    trades_as_customer: Mapped[list[Trade]] = relationship(
        foreign_keys="[Trade.customer_id]", back_populates="customer"
    )
    trades_as_supplier: Mapped[list[Trade]] = relationship(
        foreign_keys="[Trade.supplier_id]", back_populates="supplier"
    )
    bids: Mapped[list[Bid]] = relationship(
        back_populates='carrier'
    )
    drivers: Mapped[list[Driver]] = relationship(
        back_populates='carrier'
    )
    vehicles: Mapped[list[Vehicle]] = relationship(
        back_populates='carrier'
    )

    @property
    def display_name(self) -> str:
        # Показываем название компании
        return self.company_name

    def __str__(self) -> str:
        # Технический вывод для разработчика
        return f'{self.__class__.__name__} id={self.id}'

    def __repr__(self) -> str:
        # Красивый вывод для человека
        return self.display_name
