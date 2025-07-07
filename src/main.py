"""bot.py – LangGraph × TMDB × ChatGPT 映画レコメンドボット
--------------------------------------------------------
• LangGraph をステートマシンとして利用し、
• TMDB API で映画候補を取得し、
• OpenAI ChatCompletion で自然言語の推薦文を生成する。

実行方法：
$ python bot.py
"""

from __future__ import annotations

import os
import sys
from typing import Any, Dict, List

import openai
import requests
from langgraph.graph import StateGraph
from pydantic import BaseModel, Field, ValidationError

# ───────────────────────────────────────────────────────
# 0. 環境変数チェック
# ───────────────────────────────────────────────────────
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TMDB_API_KEY or not OPENAI_API_KEY:
    sys.stderr.write(
        "[ERROR] 環境変数 TMDB_API_KEY と OPENAI_API_KEY の両方を設定してください。\n"
    )
    sys.exit(1)

# OpenAI v1 ライブラリは `openai.OpenAI()` クライアントを使う実装に変更
openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
SYSTEM_MSG = "あなたは映画評論家です。"


# ───────────────────────────────────────────────────────
# 1. 状態モデル
# ───────────────────────────────────────────────────────
class ChatState(BaseModel):
    """ボット全体で共有するステート。"""

    query: str | None = Field(
        None, description="ユーザー指定のジャンルまたはキーワード"
    )
    recommendations: List[Dict[str, Any]] = Field(
        default_factory=list, description="TMDB 取得結果"
    )
    response_text: str | None = Field(
        None, description="ユーザーへ返すメッセージ (質問/回答)"
    )


# ───────────────────────────────────────────────────────
# 2. ユーティリティ関数
# ───────────────────────────────────────────────────────


def fetch_from_tmdb(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """キーワード検索で映画を取得する。例外時は空リストを返す。"""

    url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": query,
        "language": "ja-JP",
        "page": 1,
        "include_adult": False,
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get("results", [])[:limit]
    except requests.RequestException as exc:
        sys.stderr.write(f"[TMDB ERROR] {exc}\n")
        return []


def format_movie_list(movies: List[Dict[str, Any]]) -> str:
    """プロンプト用に映画リストを整形。"""

    if not movies:
        return "(該当作品なし)"

    lines: List[str] = []
    for m in movies:
        title = m.get("title") or m.get("original_title", "タイトル不明")
        year = (m.get("release_date", "")[:4]) or "----"
        overview: str = m.get("overview", "あらすじ情報なし")
        if len(overview) > 80:
            overview = overview[:77] + "..."
        lines.append(f"・{title}（{year}）: {overview}")
    return "\n".join(lines)


# ───────────────────────────────────────────────────────
# 3. LangGraph ノード
# ───────────────────────────────────────────────────────


def fetch_movies(state: ChatState) -> ChatState:
    """TMDB 検索を実行し、結果を state に格納。"""

    if not state.query:
        state.response_text = "どんなジャンルやキーワードで映画を探しましょうか？"
        return state

    state.recommendations = fetch_from_tmdb(state.query)

    if not state.recommendations:
        state.response_text = (
            "該当作品が見つかりませんでした。他のキーワードを試しますか？"
        )
    return state


def generate_answer(state: ChatState) -> ChatState:
    """OpenAI v1 クライアントで推薦文を生成し state.response_text に格納。"""

    if state.response_text:
        # すでに質問 or エラーメッセージが入っている場合はそのまま
        return state

    movies_text = format_movie_list(state.recommendations)
    prompt = (
        "ユーザーは『{query}』に関連する映画を探しています。"
        "次の候補から日本語で５本おすすめし、それぞれの魅力を簡潔に説明してください。\n\n{list}".format(
            query=state.query, list=movies_text
        )
    )

    try:
        resp = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_MSG},
                {"role": "user", "content": prompt},
            ],
            temperature=0.8,
            timeout=15,
        )
        state.response_text = resp.choices[0].message.content.strip()
    except Exception as exc:
        sys.stderr.write(f"[OpenAI ERROR] {exc}\n")
        state.response_text = (
            "映画の紹介文を生成できませんでした。時間を置いて再度お試しください。"
        )

    return state


# ───────────────────────────────────────────────────────
# 4. ステートグラフ構築
# ───────────────────────────────────────────────────────


def build_graph() -> StateGraph[ChatState]:
    graph: StateGraph[ChatState] = StateGraph(ChatState)

    graph.add_node("fetch", fetch_movies)
    graph.add_node("answer", generate_answer)

    graph.add_edge("fetch", "answer")

    graph.set_entry_point("fetch")
    graph.set_finish_point("answer")
    return graph


# ───────────────────────────────────────────────────────
# 5. CLI ループ
# ───────────────────────────────────────────────────────


def run_bot() -> None:  # pragma: no cover
    bot = build_graph().compile()

    print("映画レコメンドボットへようこそ！ (quit/exit で終了)")

    state = ChatState()
    while True:
        try:
            user_input = input("\n> ")
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if user_input.lower() in {"quit", "exit"}:
            print("Bye!")
            break

        state.query = user_input.strip()

        try:
            state = bot.invoke(state)
        except ValidationError as exc:
            sys.stderr.write(f"[STATE ERROR] {exc}\n")
            continue

        print(state["response_text"] or "(応答が生成されませんでした)")
        state["response_text"] = None


if __name__ == "__main__":
    run_bot()
