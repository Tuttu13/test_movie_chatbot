from __future__ import annotations

import readline  # noqa: F401 (for Unix history)

from .graph import bot
from .state import ChatState, UserProfile

__all__ = ["run_chat"]


def run_chat() -> None:
    """端末上で動く簡易 REPL"""

    profile = UserProfile()
    state = ChatState(profile=profile)

    print("\n=== 映画レコメンドチャットボット ===")
    print("キーワードを入力してください。'exit' で終了。\n")

    while True:
        try:
            user_in = input("YOU> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not user_in:
            continue
        if user_in.lower() in {"exit", "quit"}:
            print("Bye!")
            break

        state.current_query = user_in
        state = bot.invoke(state)


if __name__ == "__main__":
    run_chat()
