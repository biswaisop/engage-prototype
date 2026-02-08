# node/issue_detection.py

def issue_node(state: dict, llm):
    message = state["message"]

    response_text = (
        "I’m really sorry you’re facing this issue. "
        "I’m alerting a human team member right now to assist you."
    )

    return {
        **state,
        "result": {
            "intent": "ESCALATE_ISSUE",
            "response": response_text,
            "confidence": 1.0,
            "actions": [
                {
                    "type": "CREATE_ISSUE",
                    "payload": {
                        "category": "GENERAL",
                        "severity": "HIGH",
                        "auto_escalate": True,
                    },
                },
                {
                    "type": "REQUEST_HUMAN",
                    "payload": {
                        "reason": "User reported an issue",
                        "priority": "HIGH",
                    },
                },
            ],
        },
    }
