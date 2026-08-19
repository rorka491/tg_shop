from aiogram import Bot
from aiogram.types import BotCommand


async def setup_bot(bot: Bot):
    await bot.set_my_commands(
        [
            BotCommand(
                command="start",
                description="Старт",
            ),
            BotCommand(
                command="admin",
                description="Админ",
            )
        ]
    )