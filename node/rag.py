from schema import GraphOutput

def rag_node(state: dict, llm):
    response = llm.invoke(
        f"Answer the guest question clearly:\n{state['message']}"
    )

    return {
        **state,
        "result": {
            "intent": "INFORMATION_RETRIEVAL",
            "response": response.content.strip(),
            "confidence": 0.9,
            "actions": [],
        }
    }



