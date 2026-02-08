# graph.py
from langgraph.graph import StateGraph, END
from model import llm
from schema import GraphState
from node import intent_router_node
from node import rag_node
from node import lead_node
from node import issue_node
from node import handoff_node
from node import chat_node

builder = StateGraph(GraphState)

builder.add_node("intent_router", lambda s: intent_router_node(s, llm))
builder.add_node("rag_node", lambda s: rag_node(s, llm))
builder.add_node("lead_node", lambda s: lead_node(s, llm))
builder.add_node("issue_node", lambda s: issue_node(s, llm))
builder.add_node("handoff_node", lambda s: handoff_node(s, llm))
builder.add_node("chitchat_node", lambda s: chat_node(s, llm))

builder.set_entry_point("intent_router")

builder.add_conditional_edges(
    "intent_router",
    lambda x: x["next_node"]
)

builder.add_edge("rag_node", END)
builder.add_edge("lead_node", END)
builder.add_edge("issue_node", END)
builder.add_edge("handoff_node", END)
builder.add_edge("chitchat_node", END)

graph = builder.compile()
