from dishka import Provider, Scope, provide
from aiogram.types import CallbackQuery, Message, TelegramObject, User as TelegramUser

from src.models.postgres.user import User
from src.repositories.users import UserRepository

class UserProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_telegram_id(self, event: TelegramObject) -> int:
        if isinstance(event, (Message, CallbackQuery)) and event.from_user:
            return event.from_user.id
        raise ValueError("Cannot extract telegram_id from event")

    @provide(scope=Scope.REQUEST)
    async def get_current_user(
        self,
        telegram_id: int,
        repo: UserRepository,
    ) -> User:
        user = await repo.get_by_tg_id(telegram_id)

        if not user:
            raise ValueError(f"User with telegram_id {telegram_id} not found")

        return user

    

        