from sqlalchemy import select
from src.repositories.base import BaseRepository
from src.models.postgres import User

class UserRepository(BaseRepository[User]):

    async def get_by_tg_id(self, telegram_id: int) -> User | None:
        stmt = select(self.model).where(self.model.telegram_id==telegram_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_admins(self) -> list[User]:
        stmt = (
            select(self.model)
            .where(self.model.is_admin.is_(True))
        )

        result = await self.session.execute(stmt)
        return list(result.scalars().all())
