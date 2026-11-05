from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from time import monotonic

from aiogram import Bot
from aiogram.client.session.middlewares.base import NextRequestMiddlewareType
from aiogram.methods import GetUpdates, TelegramMethod
from aiogram.methods.base import TelegramType
from aiohttp import web


class PollingHealth:
    """Track real polling results without making additional Telegram requests."""

    def __init__(self, clock: Callable[[], float] = monotonic) -> None:
        self._clock = clock
        self._last_success: float | None = None
        self._failed = False
        self.stopping = False

    @property
    def reason(self) -> str:
        if self.stopping:
            return "stopping"
        if self._failed:
            return "polling_failed"
        if self._last_success is None:
            return "starting"
        if self._clock() - self._last_success > 90:
            return "polling_stale"
        return "ready"

    async def track(
        self,
        make_request: NextRequestMiddlewareType[TelegramType],
        bot: Bot,
        method: TelegramMethod[TelegramType],
    ) -> TelegramType:
        try:
            result = await make_request(bot, method)
        except Exception:
            if isinstance(method, GetUpdates):
                self._failed = True
            raise
        if isinstance(method, GetUpdates):
            self._last_success = self._clock()
            self._failed = False
        return result


def create_health_app(health: PollingHealth) -> web.Application:
    async def live(_request: web.Request) -> web.Response:
        return web.json_response({"status": "alive"})

    async def ready(_request: web.Request) -> web.Response:
        reason = health.reason
        return web.json_response(
            {"status": "ready" if reason == "ready" else "not_ready", "reason": reason},
            status=200 if reason == "ready" else 503,
        )

    app = web.Application()
    app.router.add_get("/healthz", live)
    app.router.add_get("/readyz", ready)
    return app


@asynccontextmanager
async def health_server(health: PollingHealth, port: int | None) -> AsyncIterator[None]:
    if port is None:
        yield
        return
    runner = web.AppRunner(create_health_app(health), access_log=None)
    await runner.setup()
    try:
        await web.TCPSite(runner, "127.0.0.1", port).start()
        yield
    finally:
        health.stopping = True
        await runner.cleanup()
