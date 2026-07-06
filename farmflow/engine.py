from __future__ import annotations

import math

from farmflow.fixtures import fixture_document, get_scenario, load_contract
from farmflow.models import (
    ClimateAssessment,
    DecisionStatus,
    RainfallAssessment,
    Scenario,
    VegetationAssessment,
)


def percentile_value(values: list[float], percentile: float) -> float:
    """Return a linearly interpolated percentile without external numeric libraries."""
    if not values:
        raise ValueError("A baseline must contain at least one value")
    if not 0 <= percentile <= 100:
        raise ValueError("Percentile must be between 0 and 100")
    ordered = sorted(values)
    position = (len(ordered) - 1) * percentile / 100
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return float(ordered[lower])
    weight = position - lower
    return float(ordered[lower] + (ordered[upper] - ordered[lower]) * weight)


def empirical_percentile(values: list[float], observed: float) -> float:
    below = sum(value < observed for value in values)
    equal = sum(value == observed for value in values)
    return round(100 * (below + 0.5 * equal) / len(values), 1)


def assess_rainfall(scenario: Scenario) -> RainfallAssessment:
    contract = load_contract()
    values = [value for value in scenario.rainfall_daily_mm if value is not None]
    coverage = 100 * len(values) / contract.coverage_window_days
    total = sum(values)
    baseline = fixture_document()["historical_45_day_rainfall_mm"]
    threshold = percentile_value(baseline, contract.rainfall_trigger.percentile)
    return RainfallAssessment(
        cumulative_rainfall_mm=round(total, 2),
        historical_threshold_mm=round(threshold, 2),
        rainfall_percentile=empirical_percentile(baseline, total),
        rainfall_coverage_percent=round(coverage, 1),
        trigger_met=total < threshold,
    )


def assess_vegetation(scenario: Scenario) -> VegetationAssessment:
    contract = load_contract()
    anomaly = None
    if scenario.ndvi_current is not None and scenario.ndvi_baseline:
        anomaly = round(
            (scenario.ndvi_current - scenario.ndvi_baseline) / scenario.ndvi_baseline,
            3,
        )
    return VegetationAssessment(
        ndvi_anomaly=anomaly,
        ndvi_quality_approved=scenario.ndvi_quality_approved,
        confirmation_met=bool(
            anomaly is not None
            and scenario.ndvi_quality_approved
            and anomaly < contract.vegetation_confirmation.threshold
        ),
    )


def determine_status(
    rainfall: RainfallAssessment,
    vegetation: VegetationAssessment,
) -> tuple[DecisionStatus, str, list[str]]:
    contract = load_contract()
    limitations = [
        "Synthetic fixture data is used; this is not an observed farm-loss record.",
        "Area-level climate indices may not match conditions on an individual farm.",
    ]
    if (
        rainfall.rainfall_coverage_percent
        < contract.data_quality.minimum_rainfall_coverage_percent
    ):
        limitations.append("Rainfall coverage is below the contract minimum.")
        return DecisionStatus.INSUFFICIENT_DATA, "low", limitations
    if not rainfall.trigger_met:
        return DecisionStatus.NORMAL, "high", limitations
    if vegetation.confirmation_met:
        return DecisionStatus.TRIGGERED_REVIEW, "high", limitations
    if vegetation.ndvi_quality_approved is False:
        limitations.append("The vegetation observation did not pass quality review.")
        return DecisionStatus.INSUFFICIENT_DATA, "low", limitations
    limitations.append("The vegetation signal does not confirm the rainfall signal.")
    return DecisionStatus.WATCHLIST, "medium", limitations


def assess_scenario(contract_id: str) -> ClimateAssessment:
    scenario = get_scenario(contract_id)
    rainfall = assess_rainfall(scenario)
    vegetation = assess_vegetation(scenario)
    status, confidence, limitations = determine_status(rainfall, vegetation)
    return ClimateAssessment(
        assessment_id=f"assessment-{contract_id}-v1",
        contract_id=contract_id,
        rule_contract_id=load_contract().contract_id,
        cumulative_rainfall_mm=rainfall.cumulative_rainfall_mm,
        historical_threshold_mm=rainfall.historical_threshold_mm,
        rainfall_percentile=rainfall.rainfall_percentile,
        rainfall_coverage_percent=rainfall.rainfall_coverage_percent,
        ndvi_anomaly=vegetation.ndvi_anomaly,
        ndvi_quality_approved=vegetation.ndvi_quality_approved,
        status=status,
        confidence=confidence,
        limitations=limitations,
    )

