import os
import textwrap

import openai

from state import ChatState

SYSTEM = "あなたは映画レコメンドボットです。"


def _fmt(movie):
    title = movie.get("title") or movie.get("original_title")
    year = (movie.get("release_date") or "")[:4]
    overview = movie.get("overview", "")[:80]
    return f"・『{title}』（{year}) — {overview}..."


def generate_answer(state: ChatState):
    # ① pending_question 優先
    if state.pending_question:
        return {
            "bot_msg": state.pending_question,
            "pending_question": None,  # 次ターンでは消える
        }

    # ② teach_snippet
    if state.teaching_snippet and not state.recommendations:
        return {
            "bot_msg": state.teaching_snippet,
            "teaching_snippet": None,
        }

    # ③ レコメンド結果
    if state.recommendations:
        bullets = "\n".join(_fmt(m) for m in state.recommendations)
        msg = textwrap.dedent(
            f"""\
            こちらの 5 本はいかがでしょう？

            {bullets}

            気になる作品があれば教えてください！👍/👎 の感想も歓迎です。
        """
        )
        return {
            "bot_msg": msg,
            "recommendations": None,  # 一度出したらクリア
        }

    # フォールバック
    return {"bot_msg": "うまく解析できませんでした。もう少し詳しく教えてください！"}
