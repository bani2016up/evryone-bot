FROM ghcr.io/astral-sh/uv:0.13.7@sha256:96f40d3904aad8d0bd010539001d36c8e2188b981e1334471a90c4a1d93bb490 AS uv
FROM python:3.13-slim-trixie@sha256:09a17cad02668ae61ece136b4fd36ac3849e14f670ebedb637ea3e15580525bc AS python-base

FROM python-base AS build
COPY --from=uv /uv /usr/local/bin/uv
ENV UV_PYTHON_DOWNLOADS=never \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1
WORKDIR /app
COPY pyproject.toml uv.lock .python-version README.md ./
COPY src/ ./src/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-editable

FROM build AS test
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable
COPY tests/ ./tests/
RUN uv run --no-sync pytest -q \
    && uv run --no-sync ruff check . \
    && uv run --no-sync ruff format --check .

FROM python-base AS runtime
LABEL org.opencontainers.image.source="https://github.com/bani2016up/evryone-bot"
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
RUN groupadd --gid 10001 bot \
    && useradd --uid 10001 --gid bot --no-create-home \
        --home-dir /nonexistent --shell /usr/sbin/nologin bot \
    && install -d -o bot -g bot /data
COPY --from=build /app/.venv /app/.venv
WORKDIR /data
USER 10001:10001
CMD ["evryone-bot"]
