from decimal import Decimal
from datetime import datetime
from uuid import UUID
from sqlalchemy import Boolean, DateTime, Integer, Numeric, Text, func, String
from sqlalchemy.orm import Mapped, mapped_column
from src.models.postgres.base import Base


class Product(Base):
    __tablename__ = "products"
    
    name: Mapped[str]
    description: Mapped[str | None] = mapped_column(Text)
    price: Mapped[int] = mapped_column(Integer)
    stock: Mapped[int] = mapped_column(default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    preview: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    is_delete: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
        nullable=False,
    )