from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    user_id: str = "demo"
    display_name: Optional[str] = None
    language: str = "ja-JP"
    liked_genres: List[int] = []  # TMDB genre_id
    disliked_genres: List[int] = []
    min_rating: Optional[float] = None
    watch_history: List[int] = []
    feedback: Dict[int, str] = {}


class ChatState(BaseModel):
    profile: UserProfile = Field(default_factory=UserProfile)
    current_query: str = ""
    recommendations: Optional[list] = None

    # 対話制御用
    pending_question: Optional[str] = None
    teaching_snippet: Optional[str] = None
    need_more_info: bool = False
