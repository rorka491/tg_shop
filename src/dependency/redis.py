from dishka import Provider, Scope, provide
from redis.asyncio import Redis
from src.core.config import settings

class RedisProvider(Provider):

    @provide(scope=Scope.APP)
    def redis(self) -> Redis:
        return Redis.from_url(url=settings.redis_url, decode_responses=True,)