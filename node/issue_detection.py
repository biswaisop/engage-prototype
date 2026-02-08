from schema import GraphOutput, Action

def issue_node(state, llm):
    message = state['message']
    response = llm.invoke("""
        Respond empathetically.
        Classify severity.
    """)

    return GraphOutput(
        intent="ESCALATE_ISSUE",
        response=response.content,
        confidence=0.94,
        actions=[
            Action(
                type="CREATE_ISSUE",
                payload={
                    "category": "BILLING",
                    "severity": "HIGH",
                    "auto_escalate": True
                }
            ),
            Action(
                type="REQUEST_HUMAN",
                payload={"reason": "High severity issue"}
            )
        ]
    ).model_dump()