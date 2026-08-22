import re
from collections.abc import Iterable

TRIGGER_PATTERN = re.compile(r"(?<!\w)@evryone(?!\w)", re.IGNORECASE)
USERNAME_PATTERN = re.compile(r"@[A-Za-z0-9_]{5,32}")
TELEGRAM_MESSAGE_LIMIT = 4096


def contains_trigger(text: str | None) -> bool:
    return bool(text and TRIGGER_PATTERN.search(text))


def parse_usernames(arguments: str | None) -> list[str] | None:
    if not arguments:
        return None

    values = arguments.split(", ")
    if any(not USERNAME_PATTERN.fullmatch(value) for value in values):
        return None

    return list(dict.fromkeys(value[1:].lower() for value in values))


def mention_chunks(
    usernames: Iterable[str], limit: int = TELEGRAM_MESSAGE_LIMIT
) -> list[str]:
    chunks: list[str] = []
    current: list[str] = []
    current_length = 0

    for username in usernames:
        mention = f"@{username}"
        separator_length = 2 if current else 0
        if current and current_length + separator_length + len(mention) > limit:
            chunks.append(", ".join(current))
            current = []
            current_length = 0

        current.append(mention)
        current_length += (2 if len(current) > 1 else 0) + len(mention)

    if current:
        chunks.append(", ".join(current))

    return chunks
