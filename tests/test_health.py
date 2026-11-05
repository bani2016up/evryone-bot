from unittest.mock import AsyncMock

import pytest
from aiogram.methods import GetMe, GetUpdates
from aiohttp.test_utils import TestClient, TestServer

from evryone_bot.health import PollingHealth, create_health_app


async def test_readiness_tracks_polling_failures_recovery_and_staleness() -> None:
    now = [0.0]
    health = PollingHealth(clock=lambda: now[0])
    request = AsyncMock(return_value=[])
    async with TestClient(TestServer(create_health_app(health))) as client:
        response = await client.get("/readyz")
        assert response.status == 503
        assert (await response.json())["reason"] == "starting"
        assert (await client.get("/healthz")).status == 200

        await health.track(request, None, GetUpdates())
        response = await client.get("/readyz")
        assert response.status == 200
        assert (await response.json())["status"] == "ready"

        request.side_effect = RuntimeError("sensitive upstream error")
        with pytest.raises(RuntimeError):
            await health.track(request, None, GetUpdates())
        response = await client.get("/readyz")
        assert response.status == 503
        assert await response.json() == {
            "status": "not_ready",
            "reason": "polling_failed",
        }
        assert (await client.get("/healthz")).status == 200

        request.side_effect = None
        await health.track(request, None, GetUpdates())
        assert (await client.get("/readyz")).status == 200
        now[0] = 91
        response = await client.get("/readyz")
        assert response.status == 503
        assert (await response.json())["reason"] == "polling_stale"

        health.stopping = True
        response = await client.get("/readyz")
        assert response.status == 503
        assert (await response.json())["reason"] == "stopping"


async def test_other_api_calls_do_not_mask_a_polling_failure() -> None:
    health = PollingHealth()
    request = AsyncMock(return_value=[])
    await health.track(request, None, GetMe())
    assert health.reason == "starting"
    request.side_effect = RuntimeError("polling failed")
    with pytest.raises(RuntimeError):
        await health.track(request, None, GetUpdates())
    request.side_effect = None
    await health.track(request, None, GetMe())
    assert health.reason == "polling_failed"
