"""
scorer.py — Prompt Injection Risk Scoring Engine

Combines regex-based pattern scores and Groq AI classification scores into
a single, actionable risk verdict with severity labels, confidence ratings,
explanations, and UI-ready metadata.
"""


# ═══════════════════════════════════════════════════════════════════════════════
#  CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

# ── Decision thresholds (on 0-100 scale) ──────────────────────────────────────
_BLOCK_THRESHOLD = 70.0   # risk >= 70  →  BLOCK / DANGEROUS
_WARN_THRESHOLD  = 40.0   # risk >= 40  →  WARN  / SUSPICIOUS

# ── Layer weights ─────────────────────────────────────────────────────────────
_PATTERN_WEIGHT = 0.50    # regex pattern layer contribution
_GROQ_WEIGHT    = 0.50    # Groq AI layer contribution

# ── Dual-signal boost (both layers agree) ────────────────────────────────────
_DUAL_BOOST     = 1.20    # 20% multiplier when both layers flag injection

# ── Multi-match bonus per extra pattern hit (capped) ─────────────────────────
_MULTI_MATCH_BONUS    = 0.03   # +3% per additional matched pattern
_MULTI_MATCH_MAX      = 0.15   # cap at +15% total bonus

# ── Category danger multipliers (some attacks are inherently worse) ───────────
_CATEGORY_MULTIPLIERS = {
    "data_extraction":      1.15,
    "harmful_content":      1.15,
    "privilege_escalation": 1.12,
    "prompt_extraction":    1.10,
    "instruction_override": 1.08,
    "jailbreak":            1.08,
    "indirect_injection":   1.05,
    "encoded_injection":    1.05,
    "role_override":        1.03,
    "social_engineering":   1.00,
}

# ── Severity tiers (descending) ──────────────────────────────────────────────
_SEVERITY_LEVELS = [
    (90.0, "critical"),
    (70.0, "high"),
    (40.0, "medium"),
    (0.1,  "low"),
    (0.0,  "none"),
]

# ── UI metadata per severity ─────────────────────────────────────────────────
_SEVERITY_META = {
    "critical": {"color": "#FF1744", "icon": "🔴", "label": "Critical Risk"},
    "high":     {"color": "#FF5722", "icon": "🟠", "label": "High Risk"},
    "medium":   {"color": "#FFC107", "icon": "🟡", "label": "Medium Risk"},
    "low":      {"color": "#8BC34A", "icon": "🟢", "label": "Low Risk"},
    "none":     {"color": "#4CAF50", "icon": "✅", "label": "No Risk"},
}

# ── Human-readable category labels ──────────────────────────────────────────
_CATEGORY_LABELS = {
    "instruction_override": "Instruction Override",
    "jailbreak":            "Jailbreak Attempt",
    "prompt_extraction":    "Prompt Extraction",
    "data_extraction":      "Data Extraction",
    "role_override":        "Role Override",
    "encoded_injection":    "Encoded Injection",
    "indirect_injection":   "Indirect Injection",
    "social_engineering":   "Social Engineering",
    "privilege_escalation": "Privilege Escalation",
    "harmful_content":      "Harmful Content",
}

# ── Action-specific recommendation messages ──────────────────────────────────
_RECOMMENDATIONS = {
    "BLOCK": "This prompt has been blocked. It contains patterns strongly associated "
             "with prompt injection attacks. Do not process this input.",
    "WARN":  "This prompt is suspicious. Review it carefully before allowing it. "
             "It may contain manipulation or injection techniques.",
    "ALLOW": "This prompt appears safe. No significant injection patterns detected.",
}


# ═══════════════════════════════════════════════════════════════════════════════
#  INTERNAL HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _get_severity(risk: float) -> str:
    """Map a risk percentage (0–100) to a severity label."""
    for threshold, label in _SEVERITY_LEVELS:
        if risk >= threshold:
            return label
    return "none"


def _get_confidence(pattern_score: float, groq_is_injection: bool) -> str:
    """
    Determine confidence based on layer agreement.

    - high:   both layers independently flag the prompt
    - medium: exactly one layer flags it
    - low:    neither layer flags it (clean prompt)
    """
    pattern_flags = pattern_score > 0.5
    if pattern_flags and groq_is_injection:
        return "high"
    if pattern_flags or groq_is_injection:
        return "medium"
    return "low"


def _get_multi_match_bonus(match_count: int) -> float:
    """
    Calculate bonus for multiple pattern matches.
    Each match beyond the first adds a small bonus, capped at _MULTI_MATCH_MAX.
    """
    if match_count <= 1:
        return 0.0
    extra = (match_count - 1) * _MULTI_MATCH_BONUS
    return min(extra, _MULTI_MATCH_MAX)


def _get_category_multiplier(attack_type: str) -> float:
    """Return a danger multiplier for the given attack category."""
    return _CATEGORY_MULTIPLIERS.get(attack_type, 1.0)


def _build_explanation(action: str, confidence: str, attack_type: str,
                       pattern_score: float, groq_score: float,
                       match_count: int, boost_applied: bool,
                       category_boost_applied: bool) -> str:
    """Build a concise human-readable explanation of the scoring decision."""
    parts = []

    if action == "ALLOW":
        parts.append("No significant injection signals detected.")
        if match_count > 0:
            parts.append("Minor pattern matches found but scored below threshold.")
        return " ".join(parts)

    # For WARN / BLOCK
    layer_desc = []
    if pattern_score > 0:
        layer_desc.append("regex patterns ({:.0f}%)".format(pattern_score))
    if groq_score > 0:
        layer_desc.append("AI analysis ({:.0f}%)".format(groq_score))

    if layer_desc:
        parts.append("Flagged by {}.".format(" and ".join(layer_desc)))

    label = _CATEGORY_LABELS.get(attack_type, attack_type)
    if attack_type and attack_type != "Unknown":
        parts.append('Primary threat: "{}".'.format(label))

    if match_count > 1:
        parts.append("{} injection patterns matched.".format(match_count))

    if boost_applied:
        parts.append("Dual-layer agreement boosted the score.")

    if category_boost_applied:
        parts.append("Category severity multiplier applied.")

    if confidence == "high":
        parts.append("High confidence — both detection layers agree.")
    elif confidence == "medium":
        parts.append("Medium confidence — only one detection layer triggered.")

    return " ".join(parts)


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN SCORING FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════

def calculate_risk_score(pattern_result: dict, groq_result: dict) -> dict:
    """
    Combine pattern-match and Groq AI scores into a single risk decision.

    Scoring pipeline:
        1. Weighted blend:    combined = (pattern × 0.50) + (groq × 0.50)
        2. Multi-match bonus: +3% per extra matched pattern (capped at +15%)
        3. Category boost:    multiplier for high-danger attack types
        4. Dual-signal boost: ×1.20 when both layers agree (capped at 1.0)

    Args:
        pattern_result: Output from patterns.pattern_check(). Expected keys:
                        'score'        (float 0-1)
                        'attack_type'  (str | None)
                        'matches'      (list[dict])
                        Optional: 'attack_types' (list[str])
        groq_result:    Output from Groq analysis. Expected keys:
                        'score'        (float 0-1)
                        'is_injection' (bool)
                        'attack_type'  (str | None)

    Returns:
        dict with all scoring outputs (see return statement for full schema)
    """
    # ── Extract raw inputs ────────────────────────────────────────────────────
    p = float(pattern_result.get("score", 0.0))
    g = float(groq_result.get("score", 0.0))
    groq_is_injection = bool(groq_result.get("is_injection", False))
    matches     = pattern_result.get("matches", [])
    match_count = len(matches)

    # ── Step 1: Weighted combination ──────────────────────────────────────────
    combined = (p * _PATTERN_WEIGHT) + (g * _GROQ_WEIGHT)

    # ── Step 2: Multi-match bonus ─────────────────────────────────────────────
    multi_bonus = _get_multi_match_bonus(match_count)
    combined += multi_bonus

    # ── Step 3: Category danger multiplier ────────────────────────────────────
    attack_type = (
        pattern_result.get("attack_type")
        or groq_result.get("attack_type")
        or "Unknown"
    )
    cat_mult = _get_category_multiplier(attack_type)
    category_boost_applied = cat_mult > 1.0
    if category_boost_applied:
        combined *= cat_mult

    # ── Step 4: Dual-signal boost ─────────────────────────────────────────────
    boost_applied = p > 0.5 and groq_is_injection
    if boost_applied:
        combined *= _DUAL_BOOST

    # ── Clamp and convert to percentage ───────────────────────────────────────
    combined = min(combined, 1.0)
    risk = round(combined * 100, 1)

    # ── Action / status classification ────────────────────────────────────────
    if risk >= _BLOCK_THRESHOLD:
        action, status = "BLOCK", "DANGEROUS"
    elif risk >= _WARN_THRESHOLD:
        action, status = "WARN", "SUSPICIOUS"
    else:
        action, status = "ALLOW", "SAFE"

    # ── Derived metadata ──────────────────────────────────────────────────────
    severity   = _get_severity(risk)
    confidence = _get_confidence(p, groq_is_injection)

    # All unique attack types (from patterns layer)
    attack_types = pattern_result.get("attack_types", [])
    if not attack_types and attack_type != "Unknown":
        attack_types = [attack_type]

    # Human-readable labels
    attack_label = _CATEGORY_LABELS.get(attack_type, attack_type)
    ui_meta      = _SEVERITY_META.get(severity, _SEVERITY_META["none"])

    # Percentages for individual layers
    pattern_pct = round(p * 100, 1)
    groq_pct    = round(g * 100, 1)

    # Explanation
    explanation = _build_explanation(
        action, confidence, attack_type,
        pattern_pct, groq_pct, match_count,
        boost_applied, category_boost_applied
    )

    return {
        # ── Core verdict ──────────────────────────────────────────────────
        "risk_score":      risk,
        "action":          action,
        "status":          status,
        "severity":        severity,
        "confidence":      confidence,

        # ── Individual layer scores (as %) ────────────────────────────────
        "pattern_score":   pattern_pct,
        "groq_score":      groq_pct,

        # ── Attack classification ─────────────────────────────────────────
        "attack_type":     attack_type,
        "attack_label":    attack_label,
        "attack_types":    attack_types,
        "match_count":     match_count,

        # ── Scoring breakdown ─────────────────────────────────────────────
        "dual_boost":      boost_applied,
        "category_boost":  category_boost_applied,
        "multi_match_bonus": round(multi_bonus * 100, 1),

        # ── UI metadata ──────────────────────────────────────────────────
        "ui_color":        ui_meta["color"],
        "ui_icon":         ui_meta["icon"],
        "ui_label":        ui_meta["label"],

        # ── Human-readable outputs ────────────────────────────────────────
        "explanation":     explanation,
        "recommendation":  _RECOMMENDATIONS[action],
    }
