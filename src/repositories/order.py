from uuid import UUID

from sqlalchemy import desc, select, update
from sqlalchemy.orm import selectinload

from src.models.postgres import OrderProduct
from src.enums import OrderStatus
from src.repositories.base import BaseRepository
from src.models.postgres import Order


class OrderRepository(BaseRepository[Order]): 

    async def recalculate_pending_product_price(
        self,
        product_id: UUID,
        price: int,
    ) -> None:
        stmt = (
            select(Order)
            .where(Order.status == OrderStatus.pending)
            .options(
                selectinload(Order.products),
            )
        )

        result = await self.session.scalars(stmt)
        orders = result.all()

        for order in orders:
            changed = False

            for item in order.products:
                if item.product_id == product_id:
                    item.price = price
                    changed = True

            if changed:
                order.total_price = sum(
                    item.quantity * item.price
                    for item in order.products
                )

    async def get_by_id(self, order_id: UUID) -> Order | None:
        stmt = (
            select(self.model)
            .where(self.model.id == order_id)
            .options(
                selectinload(self.model.user),
                selectinload(self.model.products)
                .selectinload(OrderProduct.product)
            )
        )

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()

    from sqlalchemy import select, desc

    async def all_user_orders(self, user_id: UUID) -> list[Order]:
        stmt = (
            select(Order)
            .where(Order.user_id == user_id)
            .order_by(
                desc(Order.created_at),
                desc(Order.id)
            )
            .options(
                selectinload(self.model.products)
                .selectinload(OrderProduct.product)
            )
        )

        result = await self.session.scalars(stmt)
        return list(result.all())


    async def get_pending_by_user_id(self, user_id: UUID) -> Order | None:
        stmt = (
            select(self.model)
            .where(
                self.model.user_id == user_id,
                self.model.status == OrderStatus.pending,
            )
            .options(
                selectinload(self.model.products)
                .selectinload(OrderProduct.product)
            )
        )

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()


    async def get_all_created_orders(self) -> list[Order]:
        stmt = (
            select(self.model)
            .where(
                self.model.status == OrderStatus.paid
            )            
            .options(
                selectinload(self.model.user),
                selectinload(self.model.products)
                .selectinload(OrderProduct.product)
            )
        ) 
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_all_complete_orders(self,) -> list[Order]:
        stmt = (
            select(self.model)
            .where(
                self.model.status == OrderStatus.completed
            )
            .options(
                selectinload(self.model.user),
                selectinload(self.model.products)
                .selectinload(OrderProduct.product)
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())