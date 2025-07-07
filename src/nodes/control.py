from ..state import ChatState

__all__ = ["decide_action"]


def decide_action(state: ChatState) -> str:
    """Return edge label for branching inside the graph."""

    if state.need_more_info:
        return "ask_clarify"
    if state.teaching_snippet and not state.recommendations:
        return "teach_user"
    return "fetch_movies"
