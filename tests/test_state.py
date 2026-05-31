from __future__ import annotations

from loom_run.state import ChatState, Message, decode_state, encode_state


def test_message_roundtrip() -> None:
    message = Message(role="tool", content="output", tool_name="search_docs")
    restored = Message.from_dict(message.to_dict())
    assert restored == message


def test_chat_state_roundtrip() -> None:
    state = ChatState(
        user_message="hello",
        messages=(Message(role="user", content="hello"),),
        tool_calls_used=1,
        max_tool_calls=3,
        final_answer=None,
        phase="think",
    )
    encoded = encode_state(state)
    restored = decode_state(encoded)
    assert restored == state
