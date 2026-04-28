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


def generate_safe_versions(original: str, matches: list) -> list:
    """
    Generate 3 different safe versions of a malicious prompt.

    Returns a list of 3 sanitized versions with different approaches:
        1. Conservative: Replace all matches with [REDACTED]
        2. Moderate: Replace with generic placeholders
        3. Aggressive: Remove matches entirely and clean up

    Args:
        original: The original prompt string.
        matches: List of match dicts from pattern_check().

    Returns:
        List of 3 safe version strings.
    """
    if not matches:
        return [original, original, original]

    # Version 1: Conservative - [REDACTED] markers
    v1 = sanitize_prompt(original, matches)
    v1 = get_safe_version(original, v1)

    # Version 2: Moderate - Replace with generic placeholders
    v2 = original
    for match_info in sorted(matches, key=lambda m: len(m.get("match", "")), reverse=True):
        matched_text = match_info.get("match", "")
        if not matched_text:
            continue
        pattern = re.escape(matched_text)
        v2 = re.sub(pattern, "[removed content]", v2, flags=re.IGNORECASE)
    v2 = re.sub(r"(\[removed content\]\s*){2,}", "[removed content] ", v2)
    v2 = re.sub(r"\s{2,}", " ", v2).strip()

    # Version 3: Aggressive - Remove entirely
    v3 = original
    for match_info in sorted(matches, key=lambda m: len(m.get("match", "")), reverse=True):
        matched_text = match_info.get("match", "")
        if not matched_text:
            continue
        pattern = re.escape(matched_text)
        v3 = re.sub(pattern, "", v3, flags=re.IGNORECASE)
    v3 = re.sub(r"\s{2,}", " ", v3).strip()

    # Check if any version is entirely empty
    versions = []
    for v in [v1, v2, v3]:
        if not v or v == "[Entire prompt contained injection patterns and was blocked]":
            versions.append("[This prompt is entirely malicious and cannot be sanitized]")
        else:
            versions.append(v)

    return versions
