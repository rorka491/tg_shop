from typing import TYPE_CHECKING
from decimal import Decimal
from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.postgres.base import Base

if TYPE_CHECKING:
    from src.models.postgres.order import Order
    from src.models.postgres.product import Product

class OrderProduct(Base):
    __tablename__ = "order_products"

    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int]
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    
    order: Mapped["Order"] = relationship(back_populates="products")
    product: Mapped["Product"] = relationship()