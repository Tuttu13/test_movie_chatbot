from __future__ import annotations

from typing import List

from state import ChatState

__all__ = ["generate_answer"]


def generate_answer(state: ChatState) -> ChatState:
    if state.pending_question:
        print(f"BOT> {state.pending_question}")
        state.pending_question = None
        return state

    if state.teaching_snippet and not state.recommendations:
        print(f"BOT> {state.teaching_snippet}")
        state.teaching_snippet = None
        return state

    if state.recommendations:
        lines: List[str] = ["おすすめ映画はこちらです:"]
        for m in state.recommendations:
            year = m.get("release_date", "")[:4]
            overview = (m.get("overview") or "").replace("\n", " ")[:60]
            lines.append(f"- {m['title']} ({year}) — {overview}…")
        if state.teaching_snippet:
            lines.append("\n豆知識: " + state.teaching_snippet)
            state.teaching_snippet = None
        print("BOT> " + "\n".join(lines))
    else:
        print("BOT> うまく見つかりませんでした。もう少し好みを教えてください！")

    state.recommendations = None
    return state
