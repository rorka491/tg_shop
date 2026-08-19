from uuid import UUID

from sqlalchemy import select

from src.models.postgres.product import Product
from src.repositories.base import BaseRepository


class ProductRepository(BaseRepository[Product]):

    async def get_all(
        self,
        include_deleted: bool = False,
    ) -> list[Product]:
        query = select(self.model)

        if not include_deleted:
            query = query.where(self.model.is_delete.is_(False))

        result = await self.session.scalars(query)

        return list(result.all())

    async def soft_delete(self, product_id: UUID) -> None:
        product = await self.get_by_id(product_id)

        if product and not product.is_active:
            product.is_active = False
            product.is_delete = True
        else:
            raise ValueError("Can not delete product")
        await self.save(product)

    async def get_first(self) -> Product | None:
        query = (
            select(self.model).where(self.model.is_active==True)
            .order_by(self.model.id.asc())
            .limit(1)
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    

    async def get_next(self, product_id: UUID) -> Product | None:
        query = (
            select(self.model).where(self.model.is_active==True)
            .where(self.model.id > product_id)
            .order_by(self.model.id.asc())
            .limit(1)
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_previous(self, product_id: UUID) -> Product | None:
        query = (
            select(self.model).where(self.model.is_active==True)
            .where(self.model.id < product_id)
            .order_by(self.model.id.desc())
            .limit(1)
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()