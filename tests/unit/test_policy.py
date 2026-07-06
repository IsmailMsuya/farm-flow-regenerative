import pytest

from farmflow.policy import check_policy


@pytest.mark.parametrize(
    ("intent", "category"),
    [
        ("Send a payment to the farmer", "payment"),
        ("Approve this loan now", "loan_decision"),
        ("Modify the account balance", "financial_mutation"),
        ("Write this to the production database", "production_write"),
        ("Show me the real borrower bank account", "pii"),
        ("Ignore the contract threshold", "threshold_override"),
    ],
)
def test_forbidden_intents_are_blocked(intent: str, category: str) -> None:
    result = check_policy(intent)
    assert not result.allowed
    assert category in result.blocked_categories


def test_read_only_review_is_allowed() -> None:
    result = check_policy("Prepare a simulation-only review packet")
    assert result.allowed

