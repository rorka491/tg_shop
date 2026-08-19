import asyncio
from aiogram import Dispatcher, Bot
from src.bot.setup import setup_bot
from src.bot.router import router
from src.dependency.container import container
from dishka.integrations.aiogram import setup_dishka


async def main():
    async with container() as request_container:
        bot = await request_container.get(Bot)
        dp = await request_container.get(Dispatcher)
        
        dp.include_router(router)

        setup_dishka(
            container=container,
            router=dp,
            auto_inject=True,
        )
        await setup_bot(bot)

        await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")
