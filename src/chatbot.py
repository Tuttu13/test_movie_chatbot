"""
chatbot.py
----------

簡易 CLI。入力を読み取り、回答を標準出力する。
"""

from __future__ import annotations

import sys

from graph import bot
from state import ChatState


def main() -> None:
    question = "丸ノ内線の遅延は？"
    init_state: ChatState = {"query": question, "operator": None, "status": None}
    result = bot.invoke(init_state)
    print(result)


if __name__ == "__main__":
    main()
