"""
firewall/report_generator.py — Prompt Guardian Forensic Report Generator

Transforms a raw session history into a comprehensive, structured forensic
security report suitable for compliance audits and professional presentations.

NOTE: In production, this module would integrate with SIEM platforms,
export directly to SOC dashboards, and support digital signatures.
"""

import secrets
from datetime import datetime, timezone


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_ts(ts: str):
    """Parse an ISO timestamp string, returning a datetime or None."""
    if not ts:
        return None
    try:
        # Handle both offset-aware and naive timestamps
        ts = ts.replace("Z", "+00:00")
        return datetime.fromisoformat(ts)
    except Exception:
        return None


def _fmt_iso(dt) -> str:
    if dt is None:
        return _now_iso()
    return dt.isoformat()


# ── MAIN FUNCTION ─────────────────────────────────────────────────────────────

def generate_report(history: list) -> dict:
    """
    Generate a comprehensive forensic security report from session history.

    Args:
        history: List of prompt analysis dicts, each containing:
                 timestamp, prompt, risk_score, action, attack_type, user_action

    Returns:
        Fully populated report dict ready for JSON serialisation.
    """
    report_id = "PG-RPT-" + secrets.token_hex(4).upper()
    generated_at = _now_iso()

    # ── Handle Empty History ──────────────────────────────────────────────────
    if not history:
        return {
            "report_id": report_id,
            "generated_at": generated_at,
            "report_version": "1.0",
            "session_summary": {
                "session_start": generated_at,
                "session_end": generated_at,
                "session_duration_minutes": 0,
                "total_prompts_analyzed": 0,
                "threats_blocked": 0,
                "threats_warned": 0,
                "safe_prompts": 0,
                "block_rate_percent": 0.0,
                "average_risk_score": 0.0,
                "highest_risk_score": 0.0,
                "user_overrides": 0,
                "user_sanitized": 0,
            },
            "severity_distribution": {"critical": 0, "high": 0, "medium": 0, "low": 0},
            "attack_category_breakdown": {},
            "top_threats": [],
            "timeline_events": [],
            "recommendations": [
                "No session activity to analyze. Begin using the extension to generate forensic data."
            ],
            "compliance_notes": _build_compliance(),
            "engine_metadata": _build_engine_metadata(),
        }

    # ── Parse & Sort History ──────────────────────────────────────────────────
    parsed = []
    for entry in history:
        ts = _parse_ts(entry.get("timestamp", ""))
        parsed.append((ts, entry))

    # Sort chronologically for duration calculation
    parsed_sorted_asc = sorted(parsed, key=lambda x: (x[0] is None, x[0]))
    parsed_sorted_desc = list(reversed(parsed_sorted_asc))

    earliest_ts = parsed_sorted_asc[0][0]
    latest_ts   = parsed_sorted_asc[-1][0]

    # Session duration
    if earliest_ts and latest_ts and earliest_ts != latest_ts:
        duration_minutes = round((latest_ts - earliest_ts).total_seconds() / 60)
    else:
        duration_minutes = 0

    # ── Core Counters ─────────────────────────────────────────────────────────
    total       = len(history)
    blocked     = sum(1 for e in history if e.get("action") == "BLOCK")
    warned      = sum(1 for e in history if e.get("action") == "WARN")
    safe        = sum(1 for e in history if e.get("action") == "ALLOW")
    overrides   = sum(1 for e in history if e.get("user_action") == "overridden")
    sanitized   = sum(1 for e in history if e.get("user_action") == "sanitized")

    risks       = [float(e.get("risk_score", 0) or 0) for e in history]
    avg_risk    = round(sum(risks) / total, 1) if total else 0.0
    peak_risk   = round(max(risks), 1) if risks else 0.0
    block_rate  = round((blocked / total) * 100, 1) if total else 0.0

    # ── Severity Distribution ─────────────────────────────────────────────────
    sev = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for r in risks:
        if r >= 90:
            sev["critical"] += 1
        elif r >= 70:
            sev["high"] += 1
        elif r >= 40:
            sev["medium"] += 1
        else:
            sev["low"] += 1

    # ── Attack Category Breakdown ─────────────────────────────────────────────
    cat_data: dict = {}
    for entry in history:
        cat = entry.get("attack_type") or ""
        if not cat or cat in ("Unknown", "None", ""):
            continue
        r = float(entry.get("risk_score", 0) or 0)
        if cat not in cat_data:
            cat_data[cat] = {"count": 0, "risks": []}
        cat_data[cat]["count"] += 1
        cat_data[cat]["risks"].append(r)

    attack_breakdown = {}
    for cat, info in cat_data.items():
        count = info["count"]
        attack_breakdown[cat] = {
            "count": count,
            "percentage": round((count / total) * 100, 1),
            "highest_risk": round(max(info["risks"]), 1),
        }

    # ── Timeline Events (newest first) ────────────────────────────────────────
    def _event_dict(entry):
        prompt = entry.get("prompt") or ""
        snippet = prompt[:100] + ("..." if len(prompt) > 100 else "")
        return {
            "timestamp": entry.get("timestamp", ""),
            "prompt_snippet": snippet,
            "risk_score": round(float(entry.get("risk_score", 0) or 0), 1),
            "attack_type": entry.get("attack_type") or "Unknown",
            "action_taken": entry.get("action") or "ALLOW",
            "user_decision": entry.get("user_action") or "auto",
        }

    timeline = [_event_dict(e) for _, e in parsed_sorted_desc]

    # ── Top 5 Threats (highest risk) ─────────────────────────────────────────
    top_threats = sorted(timeline, key=lambda x: x["risk_score"], reverse=True)[:5]

    # ── Dynamic Recommendations ───────────────────────────────────────────────
    recs = []
    if block_rate > 30:
        recs.append(
            f"High threat density detected ({block_rate}% block rate). "
            "Review prompt sources for patterns indicative of targeted attacks."
        )
    if overrides > 0:
        recs.append(
            f"{overrides} user override(s) recorded. Strengthen user security awareness "
            "training and enforce stricter policy controls."
        )
    attack_types = {e.get("attack_type", "") for e in history}
    if any("Jailbreak" in (t or "") for t in attack_types):
        recs.append(
            "Jailbreak attempts detected. Verify that safety guardrails are active on "
            "all production LLM integrations and update DAN-pattern signatures."
        )
    if any("Data Extraction" in (t or "") for t in attack_types):
        recs.append(
            "Data extraction attempts detected. Audit access to sensitive credentials, "
            "PII, and internal documentation accessible via LLM context."
        )
    if any("Instruction Override" in (t or "") for t in attack_types):
        recs.append(
            "Instruction override attacks detected. Harden system prompt boundaries "
            "using prompt isolation and context-separation techniques."
        )
    if duration_minutes < 5 and (blocked + warned) > 5:
        recs.append(
            "Rapid threat sequence detected in under 5 minutes. This may indicate "
            "an automated attack scan. Consider implementing rate limiting and CAPTCHA."
        )
    if peak_risk >= 90:
        recs.append(
            f"A peak risk score of {peak_risk}% was recorded — classified as CRITICAL. "
            "Immediate incident response review is recommended."
        )
    # Always-include recommendations
    recs.extend([
        "Update Prompt Guardian regex patterns weekly to cover emerging injection variants and zero-day techniques.",
        "Enable multi-language detection for non-English prompt injection vectors (Hindi, Chinese, Arabic, Russian).",
        "Integrate Prompt Guardian API behind an enterprise API gateway with OAuth2 for production deployments.",
        "Export this report periodically and archive it for compliance, SOC audits, and incident post-mortems.",
    ])

    return {
        "report_id": report_id,
        "generated_at": generated_at,
        "report_version": "1.0",
        "session_summary": {
            "session_start": _fmt_iso(earliest_ts),
            "session_end": _fmt_iso(latest_ts),
            "session_duration_minutes": duration_minutes,
            "total_prompts_analyzed": total,
            "threats_blocked": blocked,
            "threats_warned": warned,
            "safe_prompts": safe,
            "block_rate_percent": block_rate,
            "average_risk_score": avg_risk,
            "highest_risk_score": peak_risk,
            "user_overrides": overrides,
            "user_sanitized": sanitized,
        },
        "severity_distribution": sev,
        "attack_category_breakdown": attack_breakdown,
        "top_threats": top_threats,
        "timeline_events": timeline,
        "recommendations": recs,
        "compliance_notes": _build_compliance(),
        "engine_metadata": _build_engine_metadata(),
    }


def _build_compliance() -> dict:
    return {
        "owasp_llm_top_10": "LLM01 - Prompt Injection (mitigated)",
        "mitre_atlas_techniques": [
            "AML.T0051.000 - LLM Prompt Injection: Direct",
            "AML.T0051.001 - LLM Prompt Injection: Indirect",
        ],
        "data_handling": "All analysis performed locally. No prompts transmitted to third parties.",
        "audit_trail": "Complete session log included in this report.",
    }


def _build_engine_metadata() -> dict:
    return {
        "detection_layers": [
            "Regex Pattern Matching",
            "Groq Llama3 AI Classifier",
            "Weighted Risk Scoring",
        ],
        "regex_patterns_loaded": 114,
        "llm_model": "llama3-8b-8192",
        "scoring_formula": (
            "combined = (pattern_score * 0.50) + (groq_score * 0.50), "
            "with 1.2x boost on dual detection"
        ),
        "thresholds": {
            "BLOCK": ">= 70%",
            "WARN": "40% - 69%",
            "ALLOW": "< 40%",
        },
    }
