from __future__ import annotations

import re

from farmflow.models import PolicyGateResult

FORBIDDEN_PATTERNS = {
    "payment": r"\b(send|issue|make|process|transfer)\b.{0,24}\b(payment|money|funds)\b",
    "loan_decision": r"\b(approve|deny|reject)\b.{0,18}\b(loan|credit|financing)\b",
    "financial_mutation": r"\b(modify|change|reduce|increase)\b.{0,18}\b(balance|repayment)\b",
    "production_write": r"\b(write|update|delete)\b.{0,18}\b(production|live database)\b",
    "pii": r"\b(real borrower|bank account|national id|social security)\b",
    "threshold_override": r"\b(ignore|override|change)\b.{0,20}\b(threshold|contract rule)\b",
}


def check_policy(intent: str) -> PolicyGateResult:
    blocked = [
        category
        for category, pattern in FORBIDDEN_PATTERNS.items()
        if re.search(pattern, intent, flags=re.IGNORECASE)
    ]
    if blocked:
        return PolicyGateResult(
            allowed=False,
            reason="Request exceeds the simulation-only decision-support boundary.",
            blocked_categories=blocked,
        )
    return PolicyGateResult(
        allowed=True,
        reason="Request is limited to read-only assessment and human-review preparation.",
    )

