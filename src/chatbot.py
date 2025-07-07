from graph import bot
from state import ChatState


def run_chat() -> None:
    state = ChatState()
    print("=== 映画レコメンドチャットボット ===")
    print("キーワードを入力してください。'exit' で終了。")

    while True:
        user_in = input("\nYOU> ").strip()
        if user_in.lower() in {"exit", "quit"}:
            break

        state.current_query = user_in

        # 全ノードが ChatState を返すなら、これだけで OK
        state = bot.invoke(state)

        print(f"BOT> {state}")


if __name__ == "__main__":
    run_chat()
