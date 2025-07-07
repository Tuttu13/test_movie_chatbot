def ask_clarify(state):
    # pending_question に既に入っていればそのまま
    if not state.pending_question:
        state.pending_question = (
            "どんなジャンルの映画がお好きですか？（例: SF, アクション, コメディ）"
        )
    return {
        "pending_question": state.pending_question,
        "recommendations": None,
    }
