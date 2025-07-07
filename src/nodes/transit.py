"""
transit.py
----------

ODPT（鉄道運行情報）に関するノード群。
`USE_STUB=true` でスタブデータを、`false` で実 API を利用。
"""

from __future__ import annotations

import os
from typing import Dict, List

from state import ChatState

# ────────────────────────────────────────────────────────────────
# スタブ用ダミーデータ（開発／CI 用）
# ────────────────────────────────────────────────────────────────
STUB_DATA: List[Dict] = [
    {
        "dc:date": "2025-07-07T09:05:00+09:00",
        "odpt:operator": "odpt.Operator:TokyoMetro",
        "odpt:railway": "odpt.Railway:TokyoMetro.Marunouchi",
        "odpt:trainInformationStatus": "遅延",
        "odpt:trainInformationText": "丸ノ内線は安全確認のため全線で 10 分ほど遅延しています。",
    },
    {
        "dc:date": "2025-07-07T09:02:00+09:00",
        "odpt:operator": "odpt.Operator:Toei",
        "odpt:railway": "odpt.Railway:Toei.Asakusa",
        "odpt:trainInformationStatus": "平常運転",
        "odpt:trainInformationText": "都営浅草線は平常どおり運転しています。",
    },
]

USE_STUB: bool = os.getenv("USE_STUB", "true").lower() == "true"
ODPT_TOKEN: str | None = os.getenv("ODPT_TOKEN")


# ────────────────────────────────────────────────────────────────
# ノード 1: ユーザー入力の解析
# ────────────────────────────────────────────────────────────────
def parse_user(state: ChatState) -> ChatState:
    """
    路線キーワードから operator ID を推定し、state['operator'] に格納する。
    """
    mapping = {
        "丸ノ内": "odpt.Operator:TokyoMetro",
        "メトロ": "odpt.Operator:TokyoMetro",
        "都営": "odpt.Operator:Toei",
    }
    for kw, op in mapping.items():
        if kw in state["query"]:
            state["operator"] = op
            break
    return state


# ────────────────────────────────────────────────────────────────
# ノード 2: ODPT から運行情報を取得（またはスタブ）
# ────────────────────────────────────────────────────────────────
def fetch_train_info(state: ChatState) -> ChatState:
    """
    operator が決まっていれば運行情報を取得し、state['status'] へ格納。
    """
    operator = state.get("operator")
    if not operator:
        return state

    if USE_STUB:
        # スタブモード：メモリ内検索
        state["status"] = next(
            (rec for rec in STUB_DATA if rec["odpt:operator"] == operator), None
        )
    else:
        import requests

        url = "https://api.odpt.org/api/v4/odpt:TrainInformation"
        params = {"odpt:operator": operator, "acl:consumerKey": ODPT_TOKEN}
        response = requests.get(url, params=params, timeout=8)
        response.raise_for_status()
        state["status"] = (response.json() or [None])[0]

    return state


# ────────────────────────────────────────────────────────────────
# ノード 3: 応答生成（グラフの終点）
# ────────────────────────────────────────────────────────────────
def generate_answer(state: ChatState) -> Dict[str, str]:
    """
    state['status'] を人間向けメッセージに整形。
    LangGraph の finish ノードなので辞書を返す。
    """
    status = state.get("status")
    if not status:
        return {"answer": "申し訳ありません、対象路線が特定できませんでした。"}

    stamp = status["dc:date"]
    text = status["odpt:trainInformationText"]
    return {"answer": f"【{stamp} 現在】{text}"}
