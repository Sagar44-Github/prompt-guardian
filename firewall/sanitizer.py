"""
firewall/sanitizer.py — Prompt Sanitization Engine

Provides functions to neutralize detected injection patterns by masking
or removing malicious segments, and to generate safe versions of prompts.
"""

import re


def sanitize_prompt(prompt: str, matches: list) -> str:
    """
    Neutralize detected injection patterns in a prompt.

    Replaces every matched injection substring with a [REDACTED] marker.
    Processes longest matches first to avoid partial-overlap issues.

    Args:
        prompt:  The original prompt string.
        matches: List of match dicts from pattern_check(), each containing
                 a 'match' key with the matched substring.

    Returns:
        The prompt with all matched injection substrings replaced by [REDACTED].
    """
    if not matches:
        return prompt

    sanitized = prompt

    # Sort by match length descending to replace longest matches first
    sorted_matches = sorted(
        matches,
        key=lambda m: len(m.get("match", "")),
        reverse=True,
    )

    for match_info in sorted_matches:
        matched_text = match_info.get("match", "")
        if not matched_text:
            continue
        # Case-insensitive replacement of the matched substring
        pattern = re.escape(matched_text)
        sanitized = re.sub(pattern, "[REDACTED]", sanitized, flags=re.IGNORECASE)

    return sanitized


def get_safe_version(original: str, sanitized: str) -> str:
    """
    Generate the final safe version of a prompt.

    Rules:
        - If nothing was redacted, return original as-is.
        - If the entire prompt was redacted, return a placeholder.
        - Otherwise return the sanitized version with cleanup.

    Args:
        original:  The original prompt string.
        sanitized: The prompt after sanitize_prompt() processing.

    Returns:
        A string safe for downstream consumption.
    """
    # Nothing changed — prompt was clean
    if sanitized == original:
        return original

    # Check if the whole thing was wiped out
    cleaned = sanitized.replace("[REDACTED]", "").strip()
    if not cleaned:
        return "[Entire prompt contained injection patterns and was blocked]"

    # Collapse multiple consecutive [REDACTED] markers
    sanitized = re.sub(r"(\[REDACTED\]\s*){2,}", "[REDACTED] ", sanitized)

    # Clean up extra whitespace
    sanitized = re.sub(r"\s{2,}", " ", sanitized).strip()

    return sanitized
