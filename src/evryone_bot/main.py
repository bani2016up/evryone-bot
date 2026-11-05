import asyncio
import logging

from aiogram import Bot, Dispatcher

from evryone_bot.config import Settings
from evryone_bot.handlers import create_router
from evryone_bot.health import PollingHealth, health_server
from evryone_bot.repository import MemberRepository


async def main() -> None:
    settings = Settings.from_env()
    repository = MemberRepository(settings.database_path)
    await repository.initialize()

    dispatcher = Dispatcher()
    dispatcher.include_router(create_router(repository))

    health = PollingHealth()
    async with Bot(settings.telegram_api_key) as bot:
        bot.session.middleware(health.track)
        async with health_server(health, settings.health_port):
            try:
                await dispatcher.start_polling(bot)
            finally:
                health.stopping = True


def run() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    asyncio.run(main())


if __name__ == "__main__":
    run()
