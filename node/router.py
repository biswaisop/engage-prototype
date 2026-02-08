# node/router.py
from langchain_core.prompts import ChatPromptTemplate
from schema import IntentResult

prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are an intent classifier for a hotel AI chatbot.

Allowed intents ONLY:
- RAG_QUERY
- LEAD_CAPTURE
- ISSUE_COMPLAINT
- HANDOFF_REQUEST
- CHITCHAT
"""),
    ("human", "{message}")
])

INTENT_TO_NODE = {
    "RAG_QUERY": "rag_node",
    "LEAD_CAPTURE": "lead_node",
    "ISSUE_COMPLAINT": "issue_node",
    "HANDOFF_REQUEST": "handoff_node",
    "CHITCHAT": "chitchat_node",
}

def intent_router_node(state: dict, llm):
    message = state["message"]

    structured_llm = llm.with_structured_output(IntentResult)
    result = structured_llm.invoke(
        prompt.format_messages(message=message)
    )

    return {
        **state,
        "intent": result.intent,
        "confidence": result.confidence,
        "next_node": INTENT_TO_NODE[result.intent],
    }
