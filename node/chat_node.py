# nodes/chitchat_node.py
from schema import GraphOutput

def chat_node(state, llm):
    response = llm.invoke(state["message"])

    return GraphOutput(
        intent="CHITCHAT",
        response=response.content,
        confidence=0.7,
        actions=[]
    ).model_dump()
