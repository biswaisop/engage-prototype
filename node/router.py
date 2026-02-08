# node/router.py

from langchain_core.prompts import ChatPromptTemplate
from schema import IntentResult

# -------- Allowed FINAL intents (Graph + Backend contract) --------
FINAL_INTENTS = {
    "INFORMATION_RETRIEVAL",
    "LEAD_CAPTURE",
    "ISSUE_COMPLAINT",
    "HANDOFF_REQUEST",
    "CHAT",
}

EMERGENCY_KEYWORDS = [
    "fire", "smoke", "gas", "bleeding",
    "emergency", "help", "danger"
]

ISSUE_KEYWORDS = [
    "complaint", "problem", "issue",
    "charged", "refund", "not working",
    "bad", "worst"
]

BOOKING_KEYWORDS = [
    "book", "booking", "reserve",
    "reservation", "available", "stay"
]

DATE_KEYWORDS = [
    "jan", "feb", "mar", "apr", "may", "jun",
    "jul", "aug", "sep", "oct", "nov", "dec",
    "today", "tomorrow", "tonight"
]


# -------- Map LLM-internal labels → FINAL intents --------
INTENT_NORMALIZATION_MAP = {
    "RAG_QUERY": "INFORMATION_RETRIEVAL",
    "INFORMATION_RETRIEVAL": "INFORMATION_RETRIEVAL",
    "LEAD_CAPTURE": "LEAD_CAPTURE",
    "ISSUE_COMPLAINT": "ISSUE_COMPLAINT",
    "HANDOFF_REQUEST": "HANDOFF_REQUEST",
    "CHAT": "CHAT",
}

# -------- Prompt --------
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are an intent classifier for a hotel front-desk AI.

Classify the guest message into ONE of these intents ONLY:
- RAG_QUERY        (questions about hotel info, services, policies)
- LEAD_CAPTURE    (booking interest, pricing, availability, contact sharing)
- ISSUE_COMPLAINT (problems, complaints, dissatisfaction)
- HANDOFF_REQUEST (explicit request for a human)
- CHAT        (greetings, small talk)

Return only structured output.
Do NOT explain your reasoning.
""",
        ),
        ("human", "{message}"),
    ]
)

# -------- Router Node --------
def intent_router_node(state: dict, llm):
    message = state["message"].lower()

    # 🚨 1. EMERGENCY
    EMERGENCY = ["fire", "smoke", "gas", "bleeding", "danger", "emergency"]
    if any(k in message for k in EMERGENCY):
        return {
            **state,
            "intent": "ISSUE_COMPLAINT",
            "confidence": 1.0,
        }

    # 🧯 2. ROOM / SERVICE ISSUES (FIXED)
    ROOM_CONTEXT = [
        "room", "bathroom", "toilet", "washroom",
        "fan", "ac", "light", "tv", "bed"
    ]

    ISSUE_SIGNALS = [
        "missing", "not working", "broken",
        "doesn't work", "does not work",
        "stopped working", "damaged", "leaking",
        "no"
    ]

    # 🧼 2. HYGIENE / HOUSEKEEPING ISSUES (CRITICAL)
    HYGIENE_ISSUE_KEYWORDS = [
        "dirty", "not cleaned", "unclean", "filthy",
        "condoms", "used condoms", "trash", "garbage",
        "leftover", "stains", "smell", "bad smell",
        "hygiene", "cleaning", "housekeeping"
    ]

    ARRIVAL_CONTEXT = [
        "just got", "first time", "checked in",
        "check-in", "arrived", "booked room"
    ]

    ROOM_CONTEXT = [
        "room", "bed", "bathroom", "washroom"
    ]

    if (
        any(h in message for h in HYGIENE_ISSUE_KEYWORDS)
        and (any(a in message for a in ARRIVAL_CONTEXT) or any(r in message for r in ROOM_CONTEXT))
    ):
        return {
            **state,
            "intent": "ISSUE_COMPLAINT",
            "confidence": 0.98,
        }


    if any(r in message for r in ROOM_CONTEXT) and any(i in message for i in ISSUE_SIGNALS):
        return {
            **state,
            "intent": "ISSUE_COMPLAINT",
            "confidence": 0.95,
        }

    # 💰 3. BOOKING
    BOOKING = ["book", "booking", "reserve", "reservation", "stay"]
    DATE = ["jan", "feb", "mar", "apr", "may", "jun",
            "jul", "aug", "sep", "oct", "nov", "dec",
            "today", "tomorrow", "tonight"]

    if any(b in message for b in BOOKING) and any(d in message for d in DATE):
        return {
            **state,
            "intent": "LEAD_CAPTURE",
            "confidence": 0.95,
        }

    # 📚 4. DEFAULT → INFORMATION
    return {
        **state,
        "intent": "INFORMATION_RETRIEVAL",
        "confidence": 0.8,
    }
