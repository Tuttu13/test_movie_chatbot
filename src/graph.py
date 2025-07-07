from langgraph.graph import StateGraph

from nodes.answer import generate_answer
from nodes.clarify import ask_clarify
from nodes.control import decide_action
from nodes.fetch import fetch_movies
from nodes.nlp import parse_user
from nodes.rank import rank_movies
from nodes.teach import teach_user
from state import ChatState

__all__ = ["bot"]

builder = StateGraph(ChatState)

builder.add_node("parse_user", parse_user)
builder.add_node("decide_action", decide_action)
builder.add_node("ask_clarify", ask_clarify)
builder.add_node("teach_user", teach_user)
builder.add_node("fetch_movies", fetch_movies)
builder.add_node("rank_movies", rank_movies)
builder.add_node("generate_answer", generate_answer)

builder.add_edge("parse_user", "decide_action")

builder.add_conditional_edges(
    "decide_action",
    {
        "ask_clarify": "ask_clarify",
        "teach_user": "teach_user",
        "fetch_movies": "fetch_movies",
    },
)

builder.add_edge("ask_clarify", "generate_answer")
builder.add_edge("teach_user", "generate_answer")

builder.add_edge("fetch_movies", "rank_movies")
builder.add_edge("rank_movies", "generate_answer")

builder.set_entry_point("parse_user")
builder.set_finish_point("generate_answer")

bot = builder.compile()
