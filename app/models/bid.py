from __future__ import annotations
from typing import TYPE_CHECKING
import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.trade import Trade
    from app.models.users import User
    from app.models.shipment import WinnerShipmentDetail


class Bid(Base):
    price: Mapped[int]
    is_winner: Mapped[bool]

    carrier_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('companys.id'), nullable=False
    )
    carrier: Mapped[Company] = relationship(
        back_populates='bids'
    )
    trade_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('trades.id'), nullable=False
    )
    trade: Mapped[Trade] = relationship(
        back_populates='bids'
    )
    bid_creator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('users.id'), nullable=False
    )
    bid_creator: Mapped[User] = relationship(
        back_populates='bids'
    )
    winner_shipment_detail: Mapped[WinnerShipmentDetail] = relationship(
        back_populates='won_bid'
    )

    @property
    def __str__(self) -> str:
        return f'{self.__class__.__name__} id={self.id}'

    def __repr__(self) -> str:
        return (f'Trade.id={self.trade_id}, '
                f'Carrier={self.carrier}, '
                f'self.id={self.id}.')
