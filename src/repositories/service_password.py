from redis.asyncio import Redis
from src.utils.random_code import generate_service_password


class ServicePasswordRepository:
    KEY = "service:password"

    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self) -> str | None:
        return await self.redis.get(self.KEY) # type: ignore

    async def refresh(self) -> str:
        password = generate_service_password()
        await self.redis.set(self.KEY, password)
        return password

    async def delete(self) -> None:
        await self.redis.delete(self.KEY)
