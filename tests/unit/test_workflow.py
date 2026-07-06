from farmflow.models import UiSchema
from farmflow.workflow import DISCLAIMER, build_response


def test_packet_requires_human_review() -> None:
    response = build_response("demo_triggered")
    assert response.packet.requires_human_review is True
    assert response.packet.policy_gate_result.allowed is True
    assert response.packet.disclaimer == DISCLAIMER
    assert len(response.packet.audit_events) == 7


def test_ui_schema_is_allowlisted_and_validated() -> None:
    response = build_response("demo_normal")
    parsed = UiSchema.model_validate(response.ui.model_dump())
    assert {component.type for component in parsed.components} == {
        "warning_banner",
        "status_card",
        "metric_card",
        "line_chart",
        "evidence_list",
        "timeline",
        "review_action_panel",
    }

