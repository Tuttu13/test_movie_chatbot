from state import ChatState


def decide_action(state: ChatState):
    # ① 質問保留中 or 情報不足フラグが立っていれば clarify へ
    if state.need_more_info or state.pending_question:
        return {"_edge": "ask_clarify"}

    # ② ティーチフェーズなら teach_user へ
    if state.teaching_snippet and not state.recommendations:
        return {"_edge": "teach_user"}

    # ③ それ以外は映画検索へ
    return {"_edge": "fetch_movies"}
