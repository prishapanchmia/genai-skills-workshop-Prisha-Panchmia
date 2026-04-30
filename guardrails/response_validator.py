def is_response_safe(response: str) -> bool:
    if not response:
        return False

    lowered = response.lower()

    # Only block clearly unsafe or policy-breaking responses
    blocked_phrases = [
        "ignore instructions",
        "override system",
        "illegal",
        "harmful",
        "i am not allowed to say"
    ]

    return not any(b in lowered for b in blocked_phrases)