import re
from backend.schema.guardrails import GuardResult, GuardAction, GuardLayer

# Patterns that indicate prompt/instruction leakage
LEAK_PATTERNS = [
    r"system prompt",
    r"my instructions (are|were)",
    r"i (was|am) instructed to",
    r"as an ai language model",
    r"<user_message>",
    r"<retrieved_context>",
]

DEFAULT_FALLBACK = "I can help you with your stay — could you rephrase your question?"
DATA_LEAK_FALLBACK = "Let me check on that and get back to you shortly."


def check_prompt_leak(response_text: str) -> GuardResult:
    lower = response_text.lower()
    for pattern in LEAK_PATTERNS:
        if re.search(pattern, lower):
            return GuardResult(
                safe=False,
                action=GuardAction.BLOCK,
                layer=GuardLayer.OUTPUT_FILTER,
                reason=f"matched_leak_pattern:{pattern}",
                fallback_response=DEFAULT_FALLBACK,
            )
    return GuardResult(safe=True, action=GuardAction.ALLOW, layer=GuardLayer.OUTPUT_FILTER)


def check_cross_guest_leak(response_text: str, other_guests_identifiers: list[str]) -> GuardResult:
    """
    other_guests_identifiers: names/room numbers/phone fragments that belong
    to OTHER guests in the same hotel, pulled from your bookings collection
    for this org — NOT the current verified guest's own details.
    """
    lower = response_text.lower()
    for identifier in other_guests_identifiers:
        if identifier and identifier.lower() in lower:
            return GuardResult(
                safe=False,
                action=GuardAction.BLOCK,
                layer=GuardLayer.OUTPUT_FILTER,
                reason="cross_guest_data_leak",
                fallback_response=DATA_LEAK_FALLBACK,
            )
    return GuardResult(safe=True, action=GuardAction.ALLOW, layer=GuardLayer.OUTPUT_FILTER)


def run_output_filter(
    response_text: str,
    other_guests_identifiers: list[str] | None = None,
) -> GuardResult:
    """
    Single entrypoint the node calls. Runs all deterministic checks in order,
    returns on first failure.
    """
    leak_result = check_prompt_leak(response_text)
    if not leak_result.safe:
        return leak_result

    if other_guests_identifiers:
        cross_leak_result = check_cross_guest_leak(response_text, other_guests_identifiers)
        if not cross_leak_result.safe:
            return cross_leak_result

    return GuardResult(safe=True, action=GuardAction.ALLOW, layer=GuardLayer.OUTPUT_FILTER)