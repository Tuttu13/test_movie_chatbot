from ..state import ChatState

__all__ = ["ask_clarify"]


def ask_clarify(state: ChatState) -> ChatState:
    state.pending_question = (
        "どんなジャンルの映画がお好きですか？（例: SF, アクション, コメディ）"
    )
    return state
