from __future__ import annotations

import os
from typing import Dict, cast

import requests

from ..state import ChatState

__all__ = ["fetch_movies"]


def fetch_movies(state: ChatState) -> ChatState:
    if not state.profile.liked_genres:
        state.need_more_info = True
        return state

    url = "https://api.themoviedb.org/3/discover/movie"
    params: Dict[str, str | int | float] = {
        "api_key": os.environ.get("TMDB_API_KEY", ""),
        "language": state.profile.language,
        "with_genres": ",".join(map(str, state.profile.liked_genres)),
        "sort_by": "popularity.desc",
        "page": 1,
    }
    if state.profile.disliked_genres:
        params["without_genres"] = ",".join(map(str, state.profile.disliked_genres))
    if state.profile.min_rating is not None:
        params["vote_average.gte"] = state.profile.min_rating

    params = cast(Dict[str, str], {k: str(v) for k, v in params.items() if v})

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        state.recommendations = resp.json().get("results", [])[:5]
    except requests.HTTPError as e:
        print(f"TMDB API error: {e}\nparams={params}")
        state.recommendations = []

    return state
