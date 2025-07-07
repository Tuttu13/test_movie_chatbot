from langgraph.graph import StateGraph

from nodes import answer, clarify, control, fetch, nlp, rank, teach
from state import ChatState

# ────────────────────────────
builder = StateGraph(ChatState)

builder.add_node("parse_user", nlp.parse_user)
builder.add_node("decide_action", control.decide_action)
builder.add_node("ask_clarify", clarify.ask_clarify)
builder.add_node("teach_user", teach.teach_user)
builder.add_node("fetch_movies", fetch.fetch_movies)
builder.add_node("rank_movies", rank.rank_movies)
builder.add_node("generate_answer", answer.generate_answer)

builder.add_edge("parse_user", "decide_action")
builder.add_conditional_edges(
    "decide_action",
    {
        "ask_clarify": clarify.ask_clarify,
        "teach_user": teach.teach_user,
        "fetch_movies": fetch.fetch_movies,
    },
)
builder.add_edge("ask_clarify", "generate_answer")
builder.add_edge("teach_user", "generate_answer")
builder.add_edge("fetch_movies", "rank_movies")
builder.add_edge("rank_movies", "generate_answer")

builder.set_entry_point("parse_user")
builder.set_finish_point("generate_answer")

bot = builder.compile()
