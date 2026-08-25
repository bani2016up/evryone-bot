import asyncio
import logging

from aiogram import Bot, Dispatcher

from evryone_bot.config import Settings
from evryone_bot.handlers import create_router
from evryone_bot.repository import MemberRepository


async def main() -> None:
    settings = Settings.from_env()
    repository = MemberRepository(settings.database_path)
    await repository.initialize()

    dispatcher = Dispatcher()
    dispatcher.include_router(create_router(repository, settings.dima_msg))

    async with Bot(settings.telegram_api_key) as bot:
        await dispatcher.start_polling(bot)


def run() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    asyncio.run(main())


if __name__ == "__main__":
    run()
