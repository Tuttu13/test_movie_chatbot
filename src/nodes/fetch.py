import os

import requests

from state import ChatState


def fetch_movies(state: ChatState):
    if not state.profile.liked_genres:
        # 状態フラグで管理したい場合
        state.need_more_info = True
        return state

    url = "https://api.themoviedb.org/3/discover/movie"
    params = {
        "api_key": os.getenv("TMDB_API_KEY", ""),
        "language": state.profile.language,
        "with_genres": ",".join(map(str, state.profile.liked_genres)),
        "without_genres": ",".join(map(str, state.profile.disliked_genres)) or None,
        "vote_average.gte": state.profile.min_rating or None,
        "sort_by": "popularity.desc",
        "page": 1,
    }
    params = {k: v for k, v in params.items() if v}
    resp = requests.get(url, params=params, timeout=8)
    resp.raise_for_status()
    movies = resp.json().get("results", [])[:5]  # 上位 5 件だけ

    state.recommendations = movies
    state.need_more_info = False
    return state
