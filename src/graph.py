"""
graph.py
--------

LangGraph の状態遷移グラフを構築し、`bot` として公開する。
"""

from langgraph.graph import StateGraph

from nodes import fetch_train_info, generate_answer, parse_user
from state import ChatState

# ────────────────────────────────────────────────────────────────
# グラフ構築
# ────────────────────────────────────────────────────────────────
_builder = StateGraph(ChatState)

_builder.add_node("parse_user", parse_user)
_builder.add_node("fetch", fetch_train_info)
_builder.add_node("answer", generate_answer)

_builder.add_edge("parse_user", "fetch")
_builder.add_edge("fetch", "answer")

_builder.set_entry_point("parse_user")
_builder.set_finish_point("answer")

bot = _builder.compile()
