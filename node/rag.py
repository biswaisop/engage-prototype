from schema import GraphOutput

def rag_node(state, llm):
    message = state["message"]

    response = llm.invoke(f"""
        Answer the question using hotel knowledge.
        If unsure, say REQUEST_HUMAN.
        Question: {message}
    """)

    return GraphOutput(
        intent="INFORMATION_RETRIEVEAL",
        response=response.content,
        confidence=0.9,
        actions=[]
    ).model_dump()


