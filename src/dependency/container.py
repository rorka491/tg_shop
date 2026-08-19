from dishka import make_async_container
from dishka.integrations.aiogram import AiogramProvider
from src.dependency.redis import RedisProvider
from src.dependency.command import CommandProvider
from src.dependency.user import UserProvider
from src.dependency.bot import BotProvider
from src.dependency.sqlalchemy import SQLAlchemyProvider
from src.dependency.model import ModelProvider
from src.dependency.repository import RepositoryProvider


container = make_async_container(
    BotProvider(),
    RepositoryProvider(),
    SQLAlchemyProvider(),
    ModelProvider(),
    UserProvider(),
    CommandProvider(),
    AiogramProvider(),
    RedisProvider()
)


