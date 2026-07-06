from pathlib import Path


def test_no_forbidden_financial_action_buttons() -> None:
    frontend = Path(__file__).resolve().parents[2] / "frontend"
    combined = "\n".join(path.read_text(encoding="utf-8") for path in frontend.iterdir())
    forbidden_buttons = ["<button>Pay", ">Approve Loan<", ">Issue Credit<", ">Modify Balance<"]
    assert all(label not in combined for label in forbidden_buttons)


def test_frontend_does_not_evaluate_generated_code() -> None:
    script = (
        Path(__file__).resolve().parents[2] / "frontend" / "app.js"
    ).read_text(encoding="utf-8")
    assert "eval(" not in script
    assert "new Function" not in script

