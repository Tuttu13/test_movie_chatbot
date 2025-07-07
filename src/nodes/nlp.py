import json
import os

import openai

from state import ChatState

# ◇ ジャンル名→TMDB ID (最小セット例)
GENRE_MAP = {
    "sf": 878,
    "ＳＦ": 878,
    "sf映画": 878,
    "ホラー": 27,
    "アクション": 28,
    "コメディ": 35,
}

FUNC_SPEC = {
    "name": "update_preferences",
    "description": "Extract user movie preferences from utterance.",
    "parameters": {
        "type": "object",
        "properties": {
            "liked_genres": {"type": "array", "items": {"type": "string"}},
            "disliked_genres": {"type": "array", "items": {"type": "string"}},
            "ask": {"type": "string"},
        },
    },
}

SYSTEM = "あなたは映画好きの日本人ユーザ向けアシスタントです。"


def parse_user(state: ChatState):
    """
    GPT 4o に function-call で好み抽出を依頼し、差分 dict を返す
    """
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": state.current_query},
        ],
        tools=[{"type": "function", "function": FUNC_SPEC}],
        tool_choice="auto",
    )

    choice = resp.choices[0]
    if choice.finish_reason == "tool":
        args = json.loads(choice.message.tool_calls[0].function.arguments)
        updates: dict = {}

        # liked / disliked を ID へ変換しマージ
        def _merge(field: str, names: list[str]):
            ids = [GENRE_MAP.get(n.lower()) for n in names if GENRE_MAP.get(n.lower())]
            if ids:
                profile = updates.get("profile", state.profile).model_copy(
                    update={field: list(set(getattr(state.profile, field)) | set(ids))}
                )
                updates["profile"] = profile

        _merge("liked_genres", args.get("liked_genres", []))
        _merge("disliked_genres", args.get("disliked_genres", []))

        if ask := args.get("ask"):
            updates["pending_question"] = ask
            updates["need_more_info"] = True
        else:
            updates["need_more_info"] = False
        return updates

    # fallback: 情報不足
    return {"need_more_info": True}
