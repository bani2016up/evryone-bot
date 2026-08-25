from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

from aiogram.enums import ChatType
from aiogram.filters.command import CommandObject
from aiogram.types import Chat, Message, User

from evryone_bot.handlers import create_router


def make_message(**values: object) -> Message:
    defaults: dict[str, object] = {
        "message_id": 1,
        "date": datetime.now(UTC),
        "chat": Chat(id=-1001, type=ChatType.SUPERGROUP, title="Test"),
        "from_user": User(id=10, is_bot=False, first_name="Alice", username="alice1"),
        "text": "hello",
    }
    return Message(**(defaults | values))


async def test_add_users_command_registers_usernames() -> None:
    repository = AsyncMock()
    callback = create_router(repository).message.handlers[0].callback
    message = make_message(text="/evAddUsers @bob22, @carol3")
    command = CommandObject(prefix="/", command="evAddUsers", args="@bob22, @carol3")

    with patch.object(Message, "answer", new_callable=AsyncMock) as answer:
        await callback(message, command=command)

    repository.add_usernames.assert_awaited_once_with(-1001, ["bob22", "carol3"])
    answer.assert_awaited_once_with("Registered: @bob22, @carol3")


async def test_trigger_tracks_sender_and_replies() -> None:
    repository = AsyncMock()
    repository.usernames.return_value = ["alice1", "bob22"]
    callback = create_router(repository).message.handlers[1].callback
    message = make_message(text="Hello @everyone")

    with patch.object(Message, "answer", new_callable=AsyncMock) as answer:
        await callback(message)

    repository.save.assert_awaited_once_with(-1001, 10, "alice1")
    answer.assert_awaited_once_with("@alice1, @bob22")


async def test_migration_and_departure_are_persisted() -> None:
    repository = AsyncMock()
    callback = create_router(repository).message.handlers[1].callback
    departed = User(id=20, is_bot=False, first_name="Bob", username="bob22")
    message = make_message(
        text=None,
        migrate_from_chat_id=-999,
        left_chat_member=departed,
    )

    await callback(message)

    repository.migrate_chat.assert_awaited_once_with(-999, -1001)
    repository.remove.assert_awaited_once_with(-1001, 20, "bob22")


async def test_migrate_to_message_does_not_recreate_old_chat_member() -> None:
    repository = AsyncMock()
    callback = create_router(repository).message.handlers[1].callback
    message = make_message(text=None, migrate_to_chat_id=-2002)

    await callback(message)

    repository.migrate_chat.assert_awaited_once_with(-1001, -2002)
    repository.save.assert_not_awaited()
