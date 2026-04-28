"""
firewall — Prompt Guardian Injection Detection Engine

This package provides the core prompt injection analysis pipeline:
    - patterns    : regex-based injection pattern matching (114 patterns)
    - scorer      : multi-layer risk scoring engine
    - groq_checker: Groq AI-powered semantic analysis
    - sanitizer   : prompt sanitization utilities
    - analyzer    : main entry point that orchestrates all layers
"""

from firewall.analyzer import analyze_prompt

__all__ = ["analyze_prompt"]
