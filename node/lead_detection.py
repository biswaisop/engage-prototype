from utils import memory

LEAD_SYSTEM_PROMPT = (
    "You are a hotel booking assistant. "
    "Help guests with reservations, pricing, and availability. "
    "Politely gather contact details and booking preferences. "
    "Be warm and professional."
)


def lead_node(state, llm):
    print("lead node executed")
    """Handle booking inquiries with conversation memory."""
    query = state.get("message", "")
    
    # Get history using shared memory utility
    history = memory.get_history(state, max_turns=4)
    formatted_history = memory.format_for_llm(history)
    
    # Build messages using shared utility
    messages = memory.build_messages(
        query=query,
        system_prompt=LEAD_SYSTEM_PROMPT,
        history=formatted_history
    )
    
    response = llm.invoke(messages)
    answer = response.content if hasattr(response, "content") else str(response)
    
    return {
        **state,

        "result": {
            "intent": "LEAD_CAPTURE",
            "response": answer,
            "confidence": 0.95,
            "actions": [
                {
                    "type": "CREATE_LEAD",
                    "payload": {
                        "source": "CHAT"
                    }
                }
            ]
        }
    }