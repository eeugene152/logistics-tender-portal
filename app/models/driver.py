from __future__ import annotations
from typing import TYPE_CHECKING
import uuid
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base, str_null_false, str_uniq

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.shipment import WinnerShipmentDetail


class Driver(Base):
    first_name: Mapped[str_null_false]
    last_name: Mapped[str_null_false]
    driver_phone_number: Mapped[str_null_false]
    driver_licence_document: Mapped[str_uniq]

    carrier_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('companys.id'), nullable=False
    )
    carrier: Mapped[Company] = relationship(
        back_populates='drivers'
    )
    winner_shipment_detail: Mapped[list[WinnerShipmentDetail]] = relationship(
        back_populates='driver'
    )

    @property
    def display_name(self) -> str:
        return f'{self.first_name} {self.last_name}'

    def __str__(self) -> str:
        return f'{self.__class__.__name__} id={self.id}'

    def __repr__(self) -> str:
        return f'Водитель: {self.display_name}, id={self.id}.'
