from langchain_core.prompts import ChatPromptTemplate
from schema import GraphOutput

prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are an intent classifier for a hotel AI chatbot.

Allowed intents ONLY:
- RAG_QUERY
- LEAD_CAPTURE
- ISSUE_COMPLAINT
- HANDOFF_REQUEST
- CHITCHAT

Return JSON with:
intent, confidence (0-1)
"""),
    ("human", "{message}")
])

def intent_router_node(state, llm):
    message = state["message"]

    result = llm.invoke(
        prompt.format_messages(message=message)
    )

    parsed = eval(result.content)

    intent = parsed["intent"]

    return {
        "next_node": {
            "RAG_QUERY": "rag_node",
            "LEAD_CAPTURE": "lead_node",
            "ISSUE_COMPLAINT": "issue_node",
            "HANDOFF_REQUEST": "handoff_node",
            "CHAT": "chitchat_node"
        }[intent],
        "intent": intent,
        "confidence": parsed["confidence"]
    }