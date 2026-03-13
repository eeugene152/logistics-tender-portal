from __future__ import annotations
from datetime import date, time, datetime
from typing import Optional, TYPE_CHECKING
import uuid

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from app.core.db import Base, str_null_false, float_two_digits
from app.models.enums import TradeStatus

if TYPE_CHECKING:
    from app.models.users import User
    from app.models.company import Company
    from app.models.pallet_type import PalletType
    from app.models.location import Location
    from app.models.bid import Bid


class Trade(Base):
    cargo_info: Mapped[str_null_false]
    weight: Mapped[float_two_digits]
    pallets: Mapped[int] = mapped_column(nullable=False)
    desired_pick_up_date: Mapped[date] = mapped_column(nullable=False)
    desired_pick_up_time: Mapped[time] = mapped_column(nullable=False)
    desired_delivery_date: Mapped[date] = mapped_column(nullable=False)
    desired_delivery_time: Mapped[time] = mapped_column(nullable=False)
    bidding_ends_at: Mapped[datetime] = mapped_column(nullable=False)
    bidding_starts_at: Mapped[datetime] = mapped_column(nullable=False)
    status: Mapped[TradeStatus] = mapped_column(
        nullable=False, default=TradeStatus.DRAFT
    )
    initial_price: Mapped[Optional[int]]

    pallettype_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('pallettypes.id'), nullable=True
    )
    pallettype: Mapped[PalletType] = relationship(
        back_populates='trades'
    )
    creator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('users.id'), nullable=True
    )
    creator: Mapped[User] = relationship(
        back_populates='trades'
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('companys.id'), nullable=True
    )
    customer: Mapped[Company] = relationship(
        foreign_keys=[customer_id], back_populates='trades_as_customer'
    )
    supplier_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('companys.id'), nullable=True
    )
    supplier: Mapped[Company] = relationship(
        foreign_keys=[supplier_id], back_populates='trades_as_supplier'
    )
    pickup_location_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('locations.id'), nullable=True
    )
    pickup_location: Mapped[Location] = relationship(
        foreign_keys=[pickup_location_id], back_populates='trades_pickup'
    )
    delivery_location_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('locations.id'), nullable=True
    )
    delivery_location: Mapped[Location] = relationship(
        foreign_keys=[delivery_location_id], back_populates='trades_delivery'
    )
    bids: Mapped[list[Bid]] = relationship(
        back_populates='trade'
    )

    @property
    def display_name(self) -> str:
        return (f'{self.supplier}, '
                f'{self.customer}, '
                f'{self.desired_pick_up_date}')

    def __str__(self) -> str:
        # Технический вывод для разработчика
        return f'{self.__class__.__name__} id={self.id}'

    def __repr__(self) -> str:
        # Красивый вывод для человека
        return self.display_name
