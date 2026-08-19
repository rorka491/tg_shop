from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from dishka import Provider, Scope, provide
from redis.asyncio import Redis
from src.core.config import settings
from aiogram.fsm.storage.redis import RedisStorage
from aiogram import Bot, Dispatcher



class BotProvider(Provider):

    @provide(scope=Scope.APP)
    def redis(self) -> Redis:
        return Redis.from_url(settings.redis_url)

    @provide(scope=Scope.APP)
    def storage(self, redis: Redis) -> RedisStorage:
        return RedisStorage(redis=redis)

    @provide(scope=Scope.APP)
    def dispatcher(self, storage: RedisStorage) -> Dispatcher:
        return Dispatcher(storage=storage)

    @provide(scope=Scope.APP)
    def bot(self) -> Bot:
        return Bot(
            token=settings.telegram_token, 
            default=DefaultBotProperties(
                parse_mode=ParseMode.HTML,
            ),
        )