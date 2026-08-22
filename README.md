# Evryone Bot

A small Telegram group bot that replies with mentions of known group members when
a message contains `@evryone`.

## How it works

Telegram's Bot API does not provide a way to list every member of a group. The
bot builds its own SQLite registry from users who send messages or appear in
join events. Users without a Telegram username cannot be mentioned.

Members can also be registered manually in a group:

```text
/evAddUsers @alice_user, @bob_user
```

Usernames must start with `@`, use letters, numbers, or underscores, and contain
5 to 32 characters after `@`. Any group member can run this command.

## Setup

1. Install [uv](https://docs.astral.sh/uv/).
2. Create a bot with [@BotFather](https://t.me/BotFather) and copy its token.
3. In BotFather, run `/setprivacy`, select the bot, and choose **Disable**. This
   lets the bot observe regular group messages and build its member registry.
4. Put the token in `.env`:

```dotenv
TELEGRAM_API_KEY=your-token-here
```

5. Install dependencies and start the bot:

```bash
uv sync
uv run evryone-bot
```

The bot requires Python 3.13. `uv` installs the required Python version when it
is not already available.

## Usage

Add the bot to a group. As members talk, their current usernames are persisted
in `evryone.db`. Post a message such as:

```text
Please review this, @evryone
```

The bot replies with a comma-separated list such as:

```text
@alice_user, @bob_user
```

Long member lists are split across messages to stay within Telegram's message
size limit. If the bot has not observed or manually registered any usernames,
it does not send an empty reply.

## Development

Run tests and lint checks:

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
```
