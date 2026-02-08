from schema import GraphOutput, Action

def lead_node(state, llm):
    message = state["message"]
    response = llm.invoke(f"""
        Extract booking intent and contact info if present.
        Respond politely confirming details.
    """)
    return GraphOutput(
        intent = "CAPTURE_LEAD",
        response=response.content,
        confidence=0.08,
        actions=[
            Action(
                type="CREATE_LEAD",
                payload={
                    "intent_type":"BOOKING",
                    "source":"AI_DETECTED"
                }
            )
        ]
    ).model_dump()