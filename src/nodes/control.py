from state import ChatState


def decide_action(state: ChatState):
    """
    状態に応じて次ノード名を返す。
    LangGraph 0.5: {"to": "<edge>"} 形式が必須
    """
    if state.need_more_info:
        return {"to": "ask_clarify"}
    if state.teaching_snippet and not state.recommendations:
        return {"to": "teach_user"}
    return {"to": "fetch_movies"}
