import pytest

from evryone_bot.mentions import contains_trigger, mention_chunks, parse_usernames


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Hello @everyone", True),
        ("@EVERYONE: update", True),
        ("Hello @Evry1bot", True),
        ("Hello @EVRY1BOT", True),
        ("hello @everyone_else", False),
        ("hello @evryone", False),
        ("hello @Evry1bot_extra", False),
        (None, False),
    ],
)
def test_contains_trigger(text: str | None, expected: bool) -> None:
    assert contains_trigger(text) is expected


def test_parse_usernames() -> None:
    assert parse_usernames("@Alice_1, @bob22, @ALICE_1") == [
        "alice_1",
        "bob22",
    ]


@pytest.mark.parametrize(
    "text",
    [
        None,
        "Alice",
        "@ok_user, broken",
        "@alice,@bob22",
        "@tiny",
    ],
)
def test_parse_usernames_rejects_invalid_input(text: str | None) -> None:
    assert parse_usernames(text) is None


def test_mention_chunks_respects_limit() -> None:
    assert mention_chunks(["alice", "bob", "charlie"], limit=12) == [
        "@alice, @bob",
        "@charlie",
    ]
