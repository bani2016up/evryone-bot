# Docker deployment

The server checkout is `/srv/projects/evryone-bot` on SSH host `prfnv`.
The initial deployment prepares the image and creates the container without
starting the bot. Start it only after the owner supplies the token and requests
startup.

## Token

Edit `/srv/projects/evryone-bot/.env` on the server:

```dotenv
TELEGRAM_API_KEY=your-token-here
```

The file is readable only by root, excluded from Git, and excluded from Docker
builds. Docker Compose reads it when creating the container. Do not paste the
real token into documentation or commit it.

## Build and verify

```bash
cd /srv/projects/evryone-bot
docker compose config --quiet
docker build --target test -t evryone-bot:test .
docker compose build
docker compose create --no-build
```

The test target runs pytest and Ruff without contacting Telegram.
The runtime image contains only production Python dependencies from `uv.lock`.
Base images are pinned by digest. The container runs as UID/GID 10001 with a
read-only root filesystem. No public ports are required for Telegram polling.

## Start after approval

After the token is filled in and the owner requests startup:

```bash
cd /srv/projects/evryone-bot
docker compose up -d --no-build --force-recreate
docker compose ps
docker compose logs --tail=100 bot
```

Recreating the container is necessary after changing `.env`; restarting an
existing container does not reload its environment. Once started, the bot
restarts automatically unless explicitly stopped.

## Stop

```bash
cd /srv/projects/evryone-bot
docker compose stop bot
```

## Data and networking

SQLite is stored at `/data/evryone.db` inside the persistent Docker volume
`evryone-bot-data`. Container recreation preserves this volume. Do not use
`docker compose down --volumes` unless deleting the bot database is intended.

The container uses the server's existing VPN routing and outbound firewall.
No application proxy or inbound Nginx route is needed.

In BotFather, disable privacy mode for this bot so it can observe regular group
messages. Stop any other polling instance of the same bot before startup.
