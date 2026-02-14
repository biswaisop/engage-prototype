# node/router.py

from schema import IntentResult


FINAL_INTENTS = {
    "INFORMATION_RETRIEVAL",
    "LEAD_CAPTURE",
    "ISSUE_COMPLAINT",
    "HANDOFF_REQUEST",
    "CHAT",
}


# ---------------------------
# KEYWORD GROUPS
# ---------------------------

EMERGENCY_KEYWORDS = [
    "fire", "smoke", "gas", "bleeding",
    "emergency", "danger", "help"
]

ISSUE_KEYWORDS = [
    "complaint", "problem", "issue",
    "charged", "refund", "not working",
    "broken", "damaged", "leaking",
    "dirty", "unclean", "filthy",
    "condoms", "trash", "garbage",
    "bad smell"
]

BOOKING_ACTION_KEYWORDS = [
    "book",
    "booking",
    "reserve",
    "reservation",
    "cancel my booking",
    "modify my booking",
    "change my booking",
    "check availability",
    "availability",
]

HANDOFF_KEYWORDS = [
    "human",
    "manager",
    "agent",
    "representative",
    "real person"
]

GREETING_KEYWORDS = [
    "hi",
    "hello",
    "hey",
    "good morning",
    "good evening",
]


QUESTION_STARTERS = (
    "what", "when", "how", "where",
    "who", "can", "do", "is", "are",
    "does", "did"
)


# ---------------------------
# ROUTER NODE
# ---------------------------

def intent_router_node(state: dict, llm=None):
    message = state["message"].strip().lower()

    # 🚨 1️⃣ Emergency → ISSUE_COMPLAINT
    if any(word in message for word in EMERGENCY_KEYWORDS):
        return {
            **state,
            "intent": "ISSUE_COMPLAINT",
            "confidence": 1.0,
        }

    # 🧯 2️⃣ Explicit complaint keywords → ISSUE_COMPLAINT
    if any(word in message for word in ISSUE_KEYWORDS):
        return {
            **state,
            "intent": "ISSUE_COMPLAINT",
            "confidence": 0.95,
        }

    # 🧑‍💼 3️⃣ Explicit request for human
    if any(word in message for word in HANDOFF_KEYWORDS):
        return {
            **state,
            "intent": "HANDOFF_REQUEST",
            "confidence": 0.95,
        }

    # 💰 4️⃣ Booking / Transactional Action
    # Important: must be action-oriented, not policy questions
    if any(word in message for word in BOOKING_ACTION_KEYWORDS):
        # If it is a direct action (not a question about policy)
        if not message.startswith(QUESTION_STARTERS) and "?" not in message:
            return {
                **state,
                "intent": "LEAD_CAPTURE",
                "confidence": 0.95,
            }

    # ❓ 5️⃣ If it looks like a question → INFORMATION_RETRIEVAL
    if message.startswith(QUESTION_STARTERS) or "?" in message:
        return {
            **state,
            "intent": "INFORMATION_RETRIEVAL",
            "confidence": 0.95,
        }

    # 👋 6️⃣ Greeting
    if any(message.startswith(word) for word in GREETING_KEYWORDS):
        return {
            **state,
            "intent": "CHAT",
            "confidence": 0.9,
        }

    # 🧠 7️⃣ Default → INFORMATION_RETRIEVAL
    # Safer than defaulting to LEAD_CAPTURE
    return {
        **state,
        "intent": "INFORMATION_RETRIEVAL",
        "confidence": 0.7,
    }
