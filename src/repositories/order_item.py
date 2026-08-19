from uuid import UUID
from sqlalchemy import func, select
from src.enums import OrderStatus
from src.models.postgres.order import Order
from src.models.postgres.order_item import OrderProduct
from src.repositories.base import BaseRepository


class OrderProductRepository(BaseRepository[OrderProduct]):

    async def get_by_order_and_product(
        self,
        order_id: UUID,
        product_id: UUID,
    ) -> OrderProduct | None:
        stmt = select(self.model).where(
            self.model.order_id == order_id,
            self.model.product_id == product_id,
        )
        return await self.session.scalar(stmt)

    async def get_quantity_in_cart(
        self,
        user_id: UUID,
        product_id: UUID,
    ) -> int:
        stmt = (
            select(func.coalesce(func.sum(OrderProduct.quantity), 0))
            .join(Order, Order.id == OrderProduct.order_id)
            .where(
                Order.user_id == user_id,
                Order.status == OrderStatus.pending,
                OrderProduct.product_id == product_id,
            )
        )

        result = await self.session.execute(stmt)

        return result.scalar_one()