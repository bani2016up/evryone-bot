from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.filters import Command
from aiogram.filters.command import CommandObject
from aiogram.types import Message

from evryone_bot.mentions import contains_trigger, mention_chunks, parse_usernames
from evryone_bot.repository import MemberRepository

GROUP_CHAT_TYPES = {ChatType.GROUP, ChatType.SUPERGROUP}


def create_router(repository: MemberRepository) -> Router:
    router = Router()

    @router.message(F.text, Command("evAddUsers", ignore_case=True))
    async def add_users(message: Message, command: CommandObject) -> None:
        if message.chat.type not in GROUP_CHAT_TYPES:
            return

        if message.from_user and not message.from_user.is_bot:
            await repository.save(
                message.chat.id,
                message.from_user.id,
                message.from_user.username,
            )

        usernames = parse_usernames(command.args)
        if usernames is None:
            await message.answer("Usage: /evAddUsers @username1, @username2")
            return

        await repository.add_usernames(message.chat.id, usernames)
        await message.answer(
            f"Registered: {', '.join(f'@{name}' for name in usernames)}"
        )

    @router.message()
    async def handle_group_message(message: Message) -> None:
        if message.chat.type not in GROUP_CHAT_TYPES:
            return

        if message.migrate_to_chat_id:
            await repository.migrate_chat(message.chat.id, message.migrate_to_chat_id)
            return
        if message.migrate_from_chat_id:
            await repository.migrate_chat(message.migrate_from_chat_id, message.chat.id)

        if message.from_user and not message.from_user.is_bot:
            await repository.save(
                message.chat.id,
                message.from_user.id,
                message.from_user.username,
            )

        for member in message.new_chat_members or []:
            if not member.is_bot:
                await repository.save(message.chat.id, member.id, member.username)

        if message.left_chat_member:
            await repository.remove(
                message.chat.id,
                message.left_chat_member.id,
                message.left_chat_member.username,
            )

        text = message.text or message.caption
        if not contains_trigger(text):
            return

        for chunk in mention_chunks(await repository.usernames(message.chat.id)):
            await message.answer(chunk)

    return router
