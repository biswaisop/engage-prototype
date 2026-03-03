from typing import Optional
from model import llm
from schema import IntentResult
import json
import re

FINAL_INTENTS = {
    "INFORMATION_RETRIEVAL",
    "LEAD_CAPTURE",
    "ISSUE_COMPLAINT",
    "HANDOFF_REQUEST",
    "CHAT",
}

# ---------------------------
# SYSTEM PROMPT FOR CLASSIFICATION
# ---------------------------

INTENT_CLASSIFICATION_PROMPT = """You are an intent classification system for a hotel front desk AI assistant.

Your job is to classify user messages into exactly ONE of these intents:

## INTENTS:

1. **INFORMATION_RETRIEVAL** - User wants factual information about:
   - Hotel policies (check-in/out, smoking, pets, cancellation)
   - Amenities (pool, gym, spa, WiFi, parking)
   - Room details (types, features, capacity)
   - Location, directions, nearby attractions
   - Pricing or rates (without booking intent)
   - Follow-up questions like "tell me more", "explain", "what else"

2. **LEAD_CAPTURE** - User shows intent to:
   - Book a room or make a reservation
   - Check availability for specific dates
   - Modify or cancel an existing booking
   - Request a quote or pricing for booking
   - Provide contact details for booking follow-up

3. **ISSUE_COMPLAINT** - User reports:
   - Problems with room (dirty, broken, not working)
   - Service complaints
   - Billing disputes or wrong charges
   - Safety concerns or emergencies
   - Negative experiences

4. **HANDOFF_REQUEST** - User explicitly wants:
   - To speak with a human
   - Manager or supervisor
   - Real person instead of AI
   - Transfer to staff

5. **CHAT** - Casual conversation:
   - Greetings (hi, hello, good morning)
   - Small talk
   - Introductions (I am..., my name is...)
   - Thanks, goodbye
   - Unclear or off-topic messages
   - Single words like "ok", "sure", "clear", "yes", "no"

## RULES:
- Choose the MOST LIKELY intent based on the message
- If ambiguous between INFORMATION_RETRIEVAL and CHAT, prefer CHAT for very short/vague messages
- "tell me more" or "explain" after a policy question = INFORMATION_RETRIEVAL
- Booking-related questions WITHOUT action intent = INFORMATION_RETRIEVAL
- "I want to book" or "reserve a room" = LEAD_CAPTURE
- Single greetings or names = CHAT
- When in doubt with short unclear messages = CHAT

## OUTPUT FORMAT:
Respond with ONLY a JSON object, no other text:
{"intent": "INTENT_NAME"}"""


# ---------------------------
# FAST KEYWORD FALLBACK
# ---------------------------

EMERGENCY_KEYWORDS = ["fire", "smoke", "gas", "bleeding", "emergency", "danger"]
HANDOFF_KEYWORDS = ["human", "manager", "agent", "representative", "real person", "speak to someone"]
GREETING_PATTERNS = ["^hi$", "^hello$", "^hey$", "^good morning", "^good evening", "^good afternoon"]
CHAT_PATTERNS = ["^ok$", "^okay$", "^sure$", "^yes$", "^no$", "^thanks", "^thank you", "^bye", "^clear$", "^i am ", "^my name is "]


def fast_keyword_check(message: str) -> Optional[dict]:
    """
    Fast path for obvious intents - saves LLM calls.
    Returns None if LLM classification needed.
    """
    msg = message.strip().lower()
    
    # Emergency - always fast path
    if any(word in msg for word in EMERGENCY_KEYWORDS):
        return {"intent": "ISSUE_COMPLAINT"}
    
    # Explicit handoff request
    if any(word in msg for word in HANDOFF_KEYWORDS):
        return {"intent": "HANDOFF_REQUEST"}
    
    # Simple greetings
    for pattern in GREETING_PATTERNS:
        if re.match(pattern, msg):
            return {"intent": "CHAT"}
    
    # Simple chat patterns
    for pattern in CHAT_PATTERNS:
        if re.match(pattern, msg):
            return {"intent": "CHAT"}
    
    return None  # Needs LLM classification


# ---------------------------
# LLM CLASSIFICATION
# ---------------------------

def classify_with_llm(message: str, context:str = None) -> dict:
    """
    Use LLM to classify intent with conversation context.
    """
    # Build context from history if available
    context_str = ""
    # if history and len(history) > 0:
    #     recent = history[-4:]  # Last 2 exchanges
    #     context_parts = []
    #     for msg in recent:
    #         role = msg.get("role", "user")
    #         content = msg.get("content", "")[:150]  # Truncate for efficiency
    #         context_parts.append(f"{role.upper()}: {content}")
    #     context_str = f"\n\nRecent conversation:\n" + "\n".join(context_parts)
    if context:
        # extracting last 2 exchanges
        lines = [line.strip() for line in context.strip().split("\n") if line.strip()]
        last_2 = lines[-4:] if len(lines) >= 4 else lines
        context_str = f"\n\nRecent conversation:\n" + "\n".join(last_2)
    user_prompt = f"""Classify this message:{context_str}

Current message: "{message}"

Respond with JSON only."""

    messages = [
        {"role": "system", "content": INTENT_CLASSIFICATION_PROMPT},
        {"role": "user", "content": user_prompt}
    ]
    
    try:
        response = llm.invoke(messages)
        content = response.content if hasattr(response, "content") else str(response)
        
        # Parse JSON from response
        json_match = re.search(r'\{[^}]+\}', content)
        if json_match:
            result = json.loads(json_match.group())
            intent = result.get("intent", "CHAT").upper()
            
            # Validate intent
            if intent not in FINAL_INTENTS:
                intent = "CHAT"
            
            return {
                "intent": intent,
            }
    except Exception as e:
        print(f"LLM classification error: {e}")
    
    # Fallback
    return {"intent": "CHAT"}


# ---------------------------
# MAIN ROUTER NODE
# ---------------------------

def intent_router_node(state: dict, llm_instance=None):
    """
    Hybrid intent router:
    1. Fast keyword check for obvious cases
    2. LLM classification for nuanced cases
    """
    message = state.get("message", "").strip()
    # history = state.get("messages", [])
    context = state.get("context", "")
    
    if not message:
        return {
            **state,
            "intent": "CHAT",
        }
    
    # 1️⃣ Try fast keyword matching first
    fast_result = fast_keyword_check(message)
    if fast_result:
        print(f"[Router] Fast match: {fast_result['intent']}")
        return {
            **state,
            "intent": fast_result["intent"]
        }
    
    # 2️⃣ Use LLM for complex classification
    llm_result = classify_with_llm(message, context)
    print(f"[Router] LLM classification: {llm_result['intent']}")
    
    return {
        **state,
        "intent": llm_result["intent"],
    }


# ---------------------------
# BATCH CLASSIFICATION (OPTIONAL)
# ---------------------------

def classify_batch(messages: list[str]) -> list[dict]:
    """
    Classify multiple messages in one LLM call.
    Useful for testing or bulk processing.
    """
    batch_prompt = f"""{INTENT_CLASSIFICATION_PROMPT}

Classify each message and return a JSON array:
[{{"message": "...", "intent": "..."}}]

Messages to classify:
{json.dumps(messages, indent=2)}"""

    try:
        response = llm.invoke([{"role": "user", "content": batch_prompt}])
        content = response.content if hasattr(response, "content") else str(response)
        
        # Extract JSON array
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except Exception as e:
        print(f"Batch classification error: {e}")
    
    return [{"intent": "CHAT"} for _ in messages]
