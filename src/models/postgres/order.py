from typing import TYPE_CHECKING
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from sqlalchemy import DateTime, ForeignKey, Numeric, func, Enum, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.enums import OrderStatus
from src.models.postgres.base import Base


if TYPE_CHECKING:
    from src.models.postgres import User, OrderProduct


class Order(Base):
    __tablename__ = "orders"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))

    total_price: Mapped[int] = mapped_column(
        Integer(),
        default=0
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus), 
        default=OrderStatus.pending
    )

    user: Mapped["User"] = relationship(back_populates="orders")
    
    products: Mapped[list["OrderProduct"]] = relationship(
        back_populates="order", 
        cascade="all, delete-orphan",
    )

    pickup_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    delivery_address: Mapped[str | None] = mapped_column(
        nullable=True
    )

    delivery_at: Mapped[datetime | None] = mapped_column(
        nullable=True
    )

    # payment: Mapped["Payment | None"] = relationship(
    #     back_populates="order",
    #     uselist=False,
    # )

