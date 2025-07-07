from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field

__all__ = ["UserProfile", "ChatState"]


class UserProfile(BaseModel):
    """Long‑lived user preferences persisted between sessions."""

    user_id: str = "demo"
    display_name: Optional[str] = None
    language: str = "ja-JP"

    liked_genres: List[int] = Field(default_factory=list)  # TMDB genre IDs
    disliked_genres: List[int] = Field(default_factory=list)

    min_rating: Optional[float] = None  # vote_average threshold (0‑10)

    # Interaction history
    watch_history: List[int] = Field(default_factory=list)
    feedback: Dict[int, str] = Field(default_factory=dict)  # movie_id -> "up" | "down"


class ChatState(BaseModel):
    """Ephemeral per‑conversation state handled by LangGraph."""

    profile: UserProfile
    current_query: str = ""
    recommendations: Optional[List[Dict]] = None

    pending_question: Optional[str] = None  # bot→user follow‑up
    teaching_snippet: Optional[str] = None  # short explanation to include in reply
    need_more_info: bool = False  # ask for genre etc.
