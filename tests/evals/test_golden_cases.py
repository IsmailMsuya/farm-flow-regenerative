import json
from pathlib import Path

from farmflow.engine import assess_scenario
from farmflow.policy import check_policy
from farmflow.workflow import build_response


def test_golden_cases() -> None:
    cases = json.loads(
        (Path(__file__).with_name("golden_cases.json")).read_text(encoding="utf-8")
    )
    scenario_ids = {
        "normal": "demo_normal",
        "watchlist": "demo_watchlist",
        "triggered": "demo_triggered",
        "insufficient": "demo_insufficient",
    }
    for case in cases:
        if "expected_status" in case:
            scenario_id = scenario_ids[case["id"]]
            assessment = assess_scenario(scenario_id)
            assert assessment.status.value == case["expected_status"]
            response = build_response(scenario_id)
            observed_sequence = [
                event.agent_name
                for event in response.packet.audit_events
            ]
            assert observed_sequence == [
                "Intake Agent",
                "Climate Agent",
                "Index Agent",
                "Contract Agent",
                "Farmer Explanation Agent",
                "Policy Gate",
                "Review Agent",
            ]
        else:
            assert check_policy(case["prompt"]).allowed is False
