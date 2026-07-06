from __future__ import annotations

from datetime import UTC, datetime

from farmflow.engine import assess_scenario
from farmflow.fixtures import get_scenario, load_contract
from farmflow.models import (
    AssessmentResponse,
    AuditEvent,
    DecisionStatus,
    ReviewPacket,
    UiComponent,
    UiSchema,
)
from farmflow.policy import check_policy

DISCLAIMER = (
    "Simulation only. Not financial advice or proof of individual farm loss. "
    "No financial record is changed; human review is required."
)

NEXT_STEPS = {
    DecisionStatus.NORMAL: "No climate-relief follow-up indicated; continue routine monitoring.",
    DecisionStatus.WATCHLIST: "Continue monitoring and route conflicting evidence to a reviewer.",
    DecisionStatus.TRIGGERED_REVIEW: (
        "Prepare the pre-agreed 60-day deferral option for human follow-up only."
    ),
    DecisionStatus.INSUFFICIENT_DATA: (
        "Request manual data-quality review; take no financial action."
    ),
}


def _audit_events(assessment_id: str) -> list[AuditEvent]:
    steps = [
        ("Intake Agent", "validate_transition_contract"),
        ("Climate Agent", "read_packaged_climate_fixture"),
        ("Index Agent", "calculate_climate_indices"),
        ("Contract Agent", "evaluate_fixed_trigger"),
        ("Farmer Explanation Agent", "prepare_plain_language_explanation"),
        ("Policy Gate", "validate_review_packet"),
        ("Review Agent", "build_review_packet"),
    ]
    now = datetime.now(UTC)
    return [
        AuditEvent(
            event_id=f"{assessment_id}:event:{index}",
            timestamp=now,
            agent_name=agent,
            tool_name=tool,
            policy_result="allowed",
            output_artifact_id=assessment_id,
        )
        for index, (agent, tool) in enumerate(steps, start=1)
    ]


def _farmer_explanation(status: DecisionStatus, start: str, end: str) -> str:
    readable = status.value.replace("_", " ")
    return (
        f"This simulated assessment is {readable}. It checks a fixed rainfall rule and "
        f"a vegetation confirmation signal for {start} through {end}. The climate index "
        "does not prove loss on an individual farm. A human reviewer decides any next step."
    )


def build_response(contract_id: str) -> AssessmentResponse:
    scenario = get_scenario(contract_id)
    assessment = assess_scenario(contract_id)
    intent = f"Prepare a simulation-only human review packet for {contract_id}"
    policy = check_policy(intent)
    if not policy.allowed:
        raise PermissionError(policy.reason)

    start = scenario.coverage_start.isoformat()
    end = scenario.coverage_end.isoformat()
    explanation = _farmer_explanation(assessment.status, start, end)
    packet = ReviewPacket(
        packet_id=f"packet-{contract_id}-v1",
        contract_id=contract_id,
        assessment_id=assessment.assessment_id,
        status=assessment.status,
        recommended_next_step=NEXT_STEPS[assessment.status],
        farmer_explanation=explanation,
        reviewer_summary=(
            f"Applied {load_contract().contract_id} without changing its thresholds. "
            f"Result: {assessment.status.value}; confidence: {assessment.confidence}."
        ),
        requires_human_review=True,
        policy_gate_result=policy,
        audit_events=_audit_events(assessment.assessment_id),
        disclaimer=DISCLAIMER,
    )
    ui = UiSchema(
        components=[
            UiComponent(
                type="warning_banner",
                title="Simulation boundary",
                data={"message": DISCLAIMER},
            ),
            UiComponent(
                type="status_card",
                title="Climate assessment",
                data={
                    "status": assessment.status.value,
                    "confidence": assessment.confidence,
                    "human_review_required": True,
                },
            ),
            UiComponent(
                type="metric_card",
                title="Rainfall evidence",
                data={
                    "cumulative_mm": assessment.cumulative_rainfall_mm,
                    "threshold_mm": assessment.historical_threshold_mm,
                    "coverage_percent": assessment.rainfall_coverage_percent,
                },
            ),
            UiComponent(
                type="line_chart",
                title="45-day rainfall series",
                data={"values": scenario.rainfall_daily_mm},
            ),
            UiComponent(
                type="evidence_list",
                title="Evidence and limitations",
                data={
                    "ndvi_anomaly": assessment.ndvi_anomaly,
                    "items": assessment.limitations,
                },
            ),
            UiComponent(
                type="timeline",
                title="Audit timeline",
                data={"events": [event.model_dump(mode="json") for event in packet.audit_events]},
            ),
            UiComponent(
                type="review_action_panel",
                title="Human review",
                data={
                    "recommended_next_step": packet.recommended_next_step,
                    "allowed_outcomes": [
                        "review_pending",
                        "approved_for_follow_up",
                        "manual_review_required",
                        "declined_due_to_insufficient_evidence",
                    ],
                },
            ),
        ]
    )
    return AssessmentResponse(scenario=scenario, assessment=assessment, packet=packet, ui=ui)
