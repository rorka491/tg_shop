from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.postgres.base import Base 

class BaseRepository[Base]:

    def __init__(self, session: AsyncSession, model: type[Base]) -> None:
        self.session = session
        self.model = model

    async def create(self, **kwargs) -> Base:
        return await self.save(self.model(**kwargs))


    async def delete_by_id(self, id) -> None:
        result = await self.session.execute(delete(self.model).where(self.model.id == id)) # type: ignore
        await self.session.flush()
        return result.rowcount > 0 # type: ignore

    async def get_by_id(self, id) -> Base | None:
        return await self.session.get(self.model, id)

    async def save(self, obj: Base) -> Base:
        self.session.add(obj)
        await self.session.flush()
        return obj

    async def get_all(self) -> list[Base]:
        result = await self.session.scalars(
            select(self.model)
        )
        return list(result)
        