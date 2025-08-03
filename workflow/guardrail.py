import logging

logger = logging.getLogger(__name__)


def sanitize_input(text: str, max_length: int = 2048) -> str:
    """
    Clean and validate user input.
    """
    if not isinstance(text, str):
        logger.error("Prompt must be a string, got: %r", text)
        raise ValueError("Prompt must be a string")
    clean: str = text.replace("```", "").replace("<script>", "")
    clean = clean.strip()
    if len(clean) > max_length:
        logger.error("Input too long: length %d (max %d)", len(clean), max_length)
        raise ValueError("Input too long")
    logger.debug("Sanitized input: %r", clean)
    return clean


def filter_llm_output(text: str) -> str:
    """
    Block forbidden or unsafe terms from LLM output.
    """
    forbidden_terms: list[str] = ["password", "credit card", "attack", "hack", "api key", "access token"]
    for term in forbidden_terms:
        if term in text.lower():
            logger.error("Unsafe content detected in LLM output: %r", term)
            raise ValueError(f"Unsafe content detected: {term}")
    logger.debug("LLM output passed filtering.")
    return text
