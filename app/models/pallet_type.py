from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base, str_uniq


if TYPE_CHECKING:
    from app.models.trade import Trade


class PalletType(Base):
    pallet_type: Mapped[str_uniq]
    is_active: Mapped[bool] = mapped_column(default=True)

    trades: Mapped[list[Trade]] = relationship(
        back_populates='pallettype'
    )
