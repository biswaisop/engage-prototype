from schema import GraphOutput, Action

def lead_node(state, llm):
    message = state["message"]
    response = llm.invoke(f"""
        Extract booking intent and contact info if present.
        Respond politely confirming details.
    """)
    return {
        **state,
        "result": {
            "intent": "LEAD_CAPTURE",
            "response": "I can help you with that booking. May I have your details?",
            "confidence": 0.95,
            "actions": [
                {
                    "type": "CREATE_LEAD",
                    "payload": {
                        "date": "FEB_14",
                        "source": "CHAT"
                    }
                }
            ]
        }
    }