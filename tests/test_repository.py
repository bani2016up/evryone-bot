from pathlib import Path

import pytest

from evryone_bot.repository import MemberRepository


@pytest.fixture
async def repository(tmp_path: Path) -> MemberRepository:
    repository = MemberRepository(tmp_path / "test.db")
    await repository.initialize()
    return repository


async def test_tracks_and_updates_observed_user(repository: MemberRepository) -> None:
    await repository.save(-1001, 10, "old_name")
    await repository.save(-1001, 10, "new_name")

    assert await repository.usernames(-1001) == ["new_name"]


async def test_adds_manual_usernames_without_duplicates(
    repository: MemberRepository,
) -> None:
    await repository.add_usernames(-1001, ["alice", "Bob"])
    await repository.add_usernames(-1001, ["ALICE"])
    await repository.save(-1001, 10, "bob")

    assert await repository.usernames(-1001) == ["alice", "Bob"]


async def test_removes_departed_or_usernameless_user(
    repository: MemberRepository,
) -> None:
    await repository.add_usernames(-1001, ["alice"])
    await repository.remove(-1001, 10, "Alice")
    await repository.save(-1001, 11, "bob")
    await repository.save(-1001, 11, None)

    assert await repository.usernames(-1001) == []


async def test_migrates_chat_and_resolves_existing_members(
    repository: MemberRepository,
) -> None:
    await repository.save(-1001, 10, "old_alice")
    await repository.add_usernames(-1001, ["bob_user"])
    await repository.save(-2002, 10, "new_alice")
    await repository.add_usernames(-2002, ["BOB_USER", "charlie"])

    await repository.migrate_chat(-1001, -2002)

    assert await repository.usernames(-1001) == []
    assert await repository.usernames(-2002) == ["BOB_USER", "charlie", "old_alice"]
