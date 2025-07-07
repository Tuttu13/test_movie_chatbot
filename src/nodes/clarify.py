from state import ChatState


def ask_clarify(state: ChatState):
    # すでにpending_questionがあればそのまま
    if not state.pending_question:
        state.pending_question = (
            "どんなジャンルの映画がお好きですか？（例: SF, アクション, コメディ）"
        )
    state.recommendations = None  # 明示的に消す
    return state
