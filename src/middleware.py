from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from typing import Any, Awaitable, Callable

class TelegramUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler,
        event: TelegramObject,
        data: dict,
    ):
        if event.from_user:
            data["telegram_user_id"] = event.from_user.id

        return await handler(event, data)


class PermissionMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[
            [TelegramObject, dict[str, Any]],
            Awaitable[Any],
        ],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        try:
            return await handler(event, data)

        except PermissionError:
            if isinstance(event, Message):
                await event.answer(
                    "🔐 Сначала введите пароль доступа."
                )

            elif isinstance(event, CallbackQuery):
                await event.answer(
                    "🔐 Сначала введите пароль доступа.",
                    show_alert=True,
                )