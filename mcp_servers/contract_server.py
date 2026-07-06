from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from farmflow.engine import determine_status
from farmflow.fixtures import get_scenario, load_contract
from farmflow.models import RainfallAssessment, VegetationAssessment
from farmflow.workflow import NEXT_STEPS, build_response

mcp = FastMCP("Farm Flow Fixed Contract", json_response=True)


@mcp.tool()
def evaluate_trigger(
    contract_id: str,
    rainfall_assessment: dict[str, Any],
    vegetation_assessment: dict[str, Any],
) -> dict[str, Any]:
    """Evaluate typed assessment artifacts with the immutable packaged contract rule."""
    if contract_id != load_contract().contract_id:
        raise ValueError("Contract ID is not allowlisted")
    rainfall = RainfallAssessment.model_validate(rainfall_assessment)
    vegetation = VegetationAssessment.model_validate(vegetation_assessment)
    status, confidence, limitations = determine_status(rainfall, vegetation)
    return {
        "contract_id": contract_id,
        "status": status.value,
        "confidence": confidence,
        "limitations": limitations,
    }


@mcp.tool()
def build_review_packet(
    contract_id: str,
    assessment_id: str,
    recommended_next_step: str,
) -> dict[str, Any]:
    """Build a simulation-only packet for an existing synthetic assessment."""
    scenario = get_scenario(contract_id)
    response = build_response(scenario.contract_id)
    if response.assessment.assessment_id != assessment_id:
        raise ValueError("Assessment ID does not match the packaged scenario")
    expected = NEXT_STEPS[response.assessment.status]
    if recommended_next_step != expected:
        raise ValueError("Next step must match the deterministic status mapping")
    return response.packet.model_dump(mode="json")


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
