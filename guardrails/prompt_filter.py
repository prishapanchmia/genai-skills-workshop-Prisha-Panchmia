def is_prompt_allowed(prompt: str) -> bool:
    blocked = [
        "ignore instructions",
        "jailbreak",
        "override system",
        "act as an admin"
    ]
    return not any(b in prompt.lower() for b in blocked)