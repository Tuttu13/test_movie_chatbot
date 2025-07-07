from graph import bot
from state import ChatState


def run_chat():
    state = ChatState()
    print("=== 映画レコメンドチャットボット ===")
    print("キーワードを入力してください。'exit' で終了。")
    while True:
        user_in = input("\nYOU> ").strip()
        if user_in.lower() in {"exit", "quit"}:
            break

        state.current_query = user_in
        # LangGraph 0.5: 差分を渡す場合は dict、第1引数は existing state
        state = bot.invoke(state, {"current_query": user_in})
        bot_msg = state.get("bot_msg") if isinstance(state, dict) else state.bot_msg
        print(f"BOT> {bot_msg}")


if __name__ == "__main__":
    run_chat()
