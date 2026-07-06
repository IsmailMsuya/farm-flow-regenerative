from __future__ import annotations

import os
import sys
from pathlib import Path

from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.apps import App
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

from farmflow.engine import assess_scenario
from farmflow.fixtures import get_scenario, load_contract

ROOT = Path(__file__).resolve().parents[1]
MODEL = os.getenv("FARMFLOW_MODEL", "gemini-flash-latest")


def validate_transition_contract(contract_id: str) -> dict[str, object]:
    """Validate a synthetic contract and return its fixed rule and coverage window."""
    scenario = get_scenario(contract_id)
    contract = load_contract()
    return {
        "valid": True,
        "scenario_contract_id": scenario.contract_id,
        "rule_contract_id": contract.contract_id,
        "location_id": scenario.location_id,
        "coverage_start": scenario.coverage_start.isoformat(),
        "coverage_end": scenario.coverage_end.isoformat(),
        "mode": contract.mode,
    }


def calculate_climate_assessment(contract_id: str) -> dict[str, object]:
    """Run deterministic Python calculations for one packaged synthetic contract."""
    return assess_scenario(contract_id).model_dump(mode="json")


def _mcp_toolset(script_name: str) -> McpToolset:
    return McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command=sys.executable,
                args=[str(ROOT / "mcp_servers" / script_name)],
                cwd=str(ROOT),
            )
        )
    )


intake_agent = LlmAgent(
    name="intake_agent",
    model=MODEL,
    instruction=(
        "Validate the selected synthetic contract with validate_transition_contract. "
        "Do not analyze climate data or make a financial decision."
    ),
    tools=[validate_transition_contract],
    output_key="intake_result",
)

climate_agent = LlmAgent(
    name="climate_agent",
    model=MODEL,
    instruction=(
        "Using the validated window in {intake_result}, retrieve only packaged rainfall, "
        "vegetation, baseline, and provenance data. Never invent observations."
    ),
    tools=[_mcp_toolset("climate_server.py")],
    output_key="climate_evidence",
)

index_agent = LlmAgent(
    name="index_agent",
    model=MODEL,
    instruction=(
        "Call calculate_climate_assessment for the user's selected contract. "
        "Do not calculate or alter thresholds yourself."
    ),
    tools=[calculate_climate_assessment],
    output_key="index_result",
)

contract_agent = LlmAgent(
    name="contract_agent",
    model=MODEL,
    instruction=(
        "Use the fixed contract MCP tools to check the typed assessment in {index_result}. "
        "Never change a contract field or recommend a financial action."
    ),
    tools=[_mcp_toolset("contract_server.py")],
    output_key="contract_result",
)

farmer_explanation_agent = LlmAgent(
    name="farmer_explanation_agent",
    model=MODEL,
    instruction=(
        "Explain {contract_result} in plain language. State the data source, window, "
        "basis-risk limitation, simulation-only boundary, and human-review next step. "
        "Do not promise payment."
    ),
    output_key="farmer_explanation",
)

review_agent = LlmAgent(
    name="review_agent",
    model=MODEL,
    instruction=(
        "Create a concise review memo from {index_result}, {contract_result}, and "
        "{farmer_explanation}. It must require human review and must not approve credit, "
        "modify a balance, or initiate a payment."
    ),
    output_key="review_packet",
)

root_agent = SequentialAgent(
    name="farm_flow_regenerative",
    description="Runs the bounded climate-relief review workflow in strict order.",
    sub_agents=[
        intake_agent,
        climate_agent,
        index_agent,
        contract_agent,
        farmer_explanation_agent,
        review_agent,
    ],
)

app = App(name="app", root_agent=root_agent)

