__version__: str

def score(hypo: list[str], ref: list[str], char_level: bool = False) -> float:
    """
    Compute corpus-level WER/CER.

    Args:
        hypo: List of hypothesis strings.
        ref: List of reference strings (same length as hypo).
        char_level: If True, score by Unicode code point (CER); otherwise by word (WER).

    Returns:
        Error rate as a percentage rounded to 4 decimal places.
    """
    ...

def score_sent(hypo: str, ref: str, char_level: bool = False) -> float:
    """
    Compute sentence-level WER/CER.

    Args:
        hypo: Hypothesis string.
        ref: Reference string.
        char_level: If True, score by Unicode code point (CER); otherwise by word (WER).

    Returns:
        Error rate as a percentage rounded to 4 decimal places.
    """
    ...
