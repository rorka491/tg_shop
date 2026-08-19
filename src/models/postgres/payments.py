from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.postgres.base import Base

if TYPE_CHECKING:
    from src.models.postgres.order import Order


# class Payment(Base):
#     __tablename__ = "payments"

#     order_id: Mapped[UUID] = mapped_column(ForeignKey("orders.id"), nullable=False)
#     order: Mapped["Order"] = relationship(back_populates="payment")