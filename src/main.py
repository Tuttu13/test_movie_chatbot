"""bot.py – LangGraph × TMDB × ChatGPT 映画レコメンドボット
====================================================
LangGraph を使って TMDB から映画候補を取得し、
OpenAI でおすすめコメントを生成する CLI アプリです。

実行方法:
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

# OpenAI v1 クライアント
openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
SYSTEM_MSG = "あなたは映画評論家です。"


# ───────────────────────────────────────────────────────
# 1. ステートモデル
# ───────────────────────────────────────────────────────
class ChatState(BaseModel):
    """チャットボットが保持する状態。"""

    query: str | None = Field(None, description="検索クエリ")
    recommendations: List[Dict[str, Any]] = Field(
        default_factory=list, description="TMDB 取得結果"
    )
    response_text: str | None = Field(None, description="ユーザーへ返すメッセージ")

    class ChatState(BaseModel):
        """チャットボットが保持する状態。"""

    query: str | None = Field(None, description="検索クエリ")
    recommendations: List[Dict[str, Any]] = Field(
        default_factory=list, description="TMDB 取得結果"
    )
    response_text: str | None = Field(None, description="ユーザーへ返すメッセージ")

    # --- ヘルパー --------------------------------------------------
    @classmethod
    def from_any(cls, obj: "ChatState | Dict[str, Any]") -> "ChatState":
        """`bot.invoke` の戻り値を ChatState へ正規化。

        - そのまま `ChatState` インスタンスなら返す。
        - `{"state": ChatState}` 辞書なら中身を返す。
        - ChatState フィールドを持つ通常の dict なら `ChatState(**obj)` で復元。
        """

        if isinstance(obj, cls):
            return obj

        # パターン 1: {"state": ChatState}
        if isinstance(obj, dict) and "state" in obj and isinstance(obj["state"], cls):
            return obj["state"]

        # パターン 2: dict がそのままフィールド集合を持つ
        if isinstance(obj, dict):
            try:
                return cls(**obj)
            except Exception:  # ValidationError or TypeError
                pass

        raise TypeError(
            "Unsupported return type from graph; expected ChatState, {'state': ChatState}, or ChatState-like dict"
        )


# ───────────────────────────────────────────────────────
# 2. 補助関数
# ───────────────────────────────────────────────────────


def fetch_from_tmdb(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """TMDB で映画を検索し、上位 `limit` 件を返す。"""

    url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": query,
        "language": "ja-JP",
        "page": 1,
        "include_adult": False,
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json().get("results", [])[:limit]
    except requests.RequestException as exc:
        sys.stderr.write(f"[TMDB ERROR] {exc}\n")
        return []


def format_movie_list(movies: List[Dict[str, Any]]) -> str:
    """映画情報を箇条書き文字列へ変換。"""

    if not movies:
        return "(該当作品なし)"

    lines: List[str] = []
    for m in movies:
        title = m.get("title") or m.get("original_title", "タイトル不明")
        year = (m.get("release_date", "")[:4]) or "----"
        overview = m.get("overview", "あらすじ情報なし")
        if len(overview) > 80:
            overview = overview[:77] + "..."
        lines.append(f"・{title}（{year}）: {overview}")
    return "\n".join(lines)


# ───────────────────────────────────────────────────────
# 3. LangGraph ノード
# ───────────────────────────────────────────────────────


def fetch_movies(state: ChatState) -> ChatState:
    """TMDB から映画候補を取得して state に格納。"""

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
    """OpenAI でおすすめコメントを生成。"""

    # 質問やエラーメッセージが既にある場合はそのまま返す
    if state.response_text:
        return state

    movies_text = format_movie_list(state.recommendations)
    prompt = (
        "ユーザーは『{query}』に関連する映画を探しています。\n"
        "次の候補から日本語で５本おすすめし、それぞれの魅力を簡潔に説明してください。\n\n{list}"
    ).format(query=state.query, list=movies_text)

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
    """LangGraph のステートグラフを構築。"""

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
    """CLI ループ。毎ターン新しいクエリを処理する。"""

    bot = build_graph().compile()
    print("映画レコメンドボットへようこそ！ (quit / exit で終了)")

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

        # 新しいクエリを設定し、前回のレスポンス／推薦結果をクリア
        state.query = user_input.strip()

        try:
            result = bot.invoke(state)
            state = ChatState.from_any(result)
        except ValidationError as exc:
            sys.stderr.write(f"[STATE ERROR] {exc}\n")
            continue

        print(state.response_text or "(応答が生成されませんでした)")


if __name__ == "__main__":
    run_bot()
