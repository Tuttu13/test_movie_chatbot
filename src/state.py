"""
state.py
--------

チャットボット全体で共有するステート定義。
"""

from typing import Dict, Optional, TypedDict


class ChatState(TypedDict):
    """LangGraph で扱うステート（一種のコンテキスト）"""

    query: str  # ユーザーの質問そのもの
    operator: Optional[str]  # ODPT operator ID（例: "odpt.Operator:TokyoMetro"）
    status: Optional[Dict]  # ODPT から取得した JSON 1 レコード
