from __future__ import annotations
import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, JSON # JSON для списка ссылок на файлы
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base

if TYPE_CHECKING:
    from app.models.bid import Bid
    from app.models.driver import Driver
    from app.models.vehicle import Vehicle


class WinnerShipmentDetail(Base):
    won_bid_id: Mapped[uuid.UUID] = mapped_column(
        # Связь с конкретной ставкой (1-к-1,
        # так как у одной ставки одно исполнение)
        ForeignKey('bids.id'), unique=True, nullable=False
    )
    won_bid: Mapped[Bid] = relationship(
        back_populates='winner_shipment_detail'
    )
    driver_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey('drivers.id'), nullable=True
    )
    driver: Mapped[Driver] = relationship(
        back_populates='winner_shipment_detail'
    )
    vehicle_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey('vehicles.id'), nullable=True
    )
    vehicle: Mapped[Vehicle] = relationship(
        back_populates='winner_shipment_detail'
    )
    # Ссылки на файлы (используем JSON для списка URL)
    files_urls: Mapped[Optional[dict | list]] = mapped_column(
        JSON, nullable=True
    )

    @property
    def __str__(self) -> str:
        return f'{self.__class__.__name__} id={self.id}'

    def __repr__(self) -> str:
        return f'{self.won_bid.__repr__}. won_id={self.id}'
