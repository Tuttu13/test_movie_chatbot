from ..state import ChatState

__all__ = ["teach_user"]


def teach_user(state: ChatState) -> ChatState:
    term = state.teaching_snippet or "映画用語"
    state.teaching_snippet = (
        f"『{term}』は映画に関する用語です。（詳しい説明をここに挿入）"
    )
    return state
