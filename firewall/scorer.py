"""
firewall/scorer.py — Re-exports from the root scorer module.

The core scoring logic lives in the root-level scorer.py.
This module re-exports it for the firewall package.
"""

from scorer import calculate_risk_score

__all__ = ["calculate_risk_score"]
