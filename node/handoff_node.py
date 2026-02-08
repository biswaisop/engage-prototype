# nodes/handoff_node.py
from schema import GraphOutput, Action

def handoff_node(state, llm):
    return GraphOutput(
        intent="REQUEST_HUMAN",
        response="I'm connecting you with a human agent now.",
        confidence=1.0,
        actions=[
            Action(
                type="INITIATE_HANDOFF",
                payload={"priority": "NORMAL"}
            )
        ]
    ).model_dump()
