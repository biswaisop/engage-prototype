import json
import re

LEAD_SYSTEM_PROMPT = """You are a hotel booking assistant.
The user is interested in making a reservation or has asked about booking.

Analyze the conversation history and the user's latest message.
1. If the user is asking to book but hasn't explicitly confirmed yet, ask them clearly: "Would you like to proceed with booking a room?"
2. If the assistant previously asked if they want to book, and the user just confirmed (e.g., "yes", "sure", "ok"), you MUST trigger the booking form.
3. If the user explicitly asks to book and confirms in a single message (e.g., "I want to book a room right now"), trigger the booking form.

Respond ONLY with a JSON object in this format:
{
    "response": "Your conversational response to the user here.",
    "trigger_form": true or false
}"""

def lead_node(state, llm):
    print("lead node executed")
    query = state.get("message", "")
    context = state.get("context", "")
    
    prompt = f"{LEAD_SYSTEM_PROMPT}\n\nConversation history:\n{context}\n\nUser: {query}"
    
    response = llm.invoke(prompt)
    answer = response.content if hasattr(response, "content") else str(response)
    
    trigger_form = False
    text_response = "I'd be happy to help you with booking. Would you like to proceed?"
    
    try:
        json_match = re.search(r'\{.*\}', answer, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group())
            text_response = parsed.get("response", text_response)
            trigger_form = parsed.get("trigger_form", False)
        else:
            text_response = answer
    except Exception as e:
        print(f"Lead parsing error: {e}")
        text_response = answer

    actions = []
    if trigger_form:
        actions.append({
            "type": "SERVE_WIDGET",
            "payload": {
                "widget_type": "LEAD_FORM"
            }
        })
    else:
        actions.append({
            "type": "CREATE_LEAD",
            "payload": {
                "source": "CHAT",
                "status": "PENDING_CONFIRMATION"
            }
        })

    return {
        **state,
        "result": {
            "intent": "LEAD_CAPTURE",
            "response": text_response,
            "actions": actions
        }
    }