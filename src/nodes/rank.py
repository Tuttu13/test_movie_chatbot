def rank_movies(state):
    print("test")
    # 例えば、vote_average順にソート（降順）
    if state.recommendations:
        state.recommendations = sorted(
            state.recommendations, key=lambda x: x.get("vote_average", 0), reverse=True
        )
    return state
