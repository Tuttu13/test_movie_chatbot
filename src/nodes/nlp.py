from __future__ import annotations

import re

from ..state import ChatState

__all__ = ["parse_user"]

# Simple keyword helpers (Japanese)
_KW_GENRE_SF = re.compile(r"sf|sci[- ]?fi|ＳＦ", re.I)
_KW_GENRE_HORROR_DISLIKE = re.compile(r"ホラー.*嫌|怖い.*無理", re.I)
_KW_WHAT_IS = re.compile(r"(.*?)(って何|とは何|とは？|とは)\??")


def parse_user(state: ChatState) -> ChatState:
    """Detect preference statements or definition requests (very naive)."""

    text = state.current_query

    # Definition intent
    m = _KW_WHAT_IS.search(text)
    if m:
        state.teaching_snippet = m.group(1).strip() or "用語"
        return state

    # Preferences
    if _KW_GENRE_HORROR_DISLIKE.search(text):
        state.profile.disliked_genres.append(27)  # Horror genre ID
    if _KW_GENRE_SF.search(text):
        state.profile.liked_genres.append(878)  # Sci‑Fi genre ID

    state.need_more_info = not (
        state.profile.liked_genres or state.profile.disliked_genres
    )
