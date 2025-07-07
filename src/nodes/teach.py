import os

import openai

from state import ChatState

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
                "content": f"『{term}』とは何ですか？200 字で日本語で解説してください",
            },
        ],
    )
    snippet = resp.choices[0].message.content.strip()

    # 解説に加えて「次に何を入力してほしいか」を質問文で返す
    follow_up = "どんなジャンルや気分の映画が観たいか、教えてください！"

    state.bot_msg = f"{snippet}\n\n{follow_up}"
    state.teaching_snippet = None  # 解説済みなのでクリア
    state.pending_question = follow_up
    state.need_more_info = True  # ← 追加で欲しい情報がある

    return state
