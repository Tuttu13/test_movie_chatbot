import os

import openai

from ..state import ChatState

SYSTEM = "あなたは映画評論家です。"


def teach_user(state: ChatState):
    term = state.teaching_snippet or "映画"
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM},
            {
                "role": "user",
                "content": f"『{term}』とは何ですか？200 字で日本語解説してください",
            },
        ],
    )
    snippet = resp.choices[0].message.content.strip()
    return {
        "teaching_snippet": snippet,
        "pending_question": None,
    }
