from __future__ import annotations

import json
from datetime import timedelta
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import TypeAdapter

from farmflow.models import Scenario, TransitionContract

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS_PATH = ROOT / "data" / "fixtures" / "scenarios.json"
CONTRACT_PATH = ROOT / "contracts" / "kenya_regenerative_transition_v1.yaml"
PROVENANCE_PATH = ROOT / "data" / "provenance" / "datasets.yaml"
ALLOWED_LOCATION_IDS = {"western_kenya_demo_001"}


@lru_cache
def fixture_document() -> dict[str, Any]:
    return json.loads(SCENARIOS_PATH.read_text(encoding="utf-8"))


@lru_cache
def load_scenarios() -> tuple[Scenario, ...]:
    adapter = TypeAdapter(list[Scenario])
    return tuple(adapter.validate_python(fixture_document()["scenarios"]))


def get_scenario(contract_id: str) -> Scenario:
    for scenario in load_scenarios():
        if scenario.contract_id == contract_id:
            return scenario
    raise ValueError(f"Unknown synthetic contract: {contract_id}")


@lru_cache
def load_contract() -> TransitionContract:
    return TransitionContract.model_validate(
        yaml.safe_load(CONTRACT_PATH.read_text(encoding="utf-8"))
    )


@lru_cache
def load_provenance() -> dict[str, Any]:
    return yaml.safe_load(PROVENANCE_PATH.read_text(encoding="utf-8"))


def list_portfolio() -> list[dict[str, Any]]:
    return [
        {
            "contract_id": item.contract_id,
            "farmer_alias": item.farmer_alias,
            "location_id": item.location_id,
            "crop": load_contract().crop,
            "practices": [
                "maize-bean intercrop",
                "residue retention",
                "reduced soil disturbance",
                "organic amendments",
            ],
            "coverage_start": item.coverage_start.isoformat(),
            "coverage_end": item.coverage_end.isoformat(),
        }
        for item in load_scenarios()
    ]


def _validate_location(location_id: str) -> None:
    if location_id not in ALLOWED_LOCATION_IDS:
        raise ValueError(f"Location is not allowlisted: {location_id}")


def scenario_for_window(location_id: str, start_date: str, end_date: str) -> Scenario:
    _validate_location(location_id)
    for scenario in load_scenarios():
        if (
            scenario.location_id == location_id
            and scenario.coverage_start.isoformat() == start_date
            and scenario.coverage_end.isoformat() == end_date
        ):
            return scenario
    raise ValueError("Date range is not present in the packaged fixture")


def rainfall_series(location_id: str, start_date: str, end_date: str) -> list[dict[str, Any]]:
    scenario = scenario_for_window(location_id, start_date, end_date)
    return [
        {
            "date": (scenario.coverage_start + timedelta(days=index)).isoformat(),
            "rainfall_mm": value,
            "quality_flag": "approved" if value is not None else "missing",
            "dataset_name": "chirps_rainfall_demo",
            "dataset_version": "synthetic-v1",
        }
        for index, value in enumerate(scenario.rainfall_daily_mm)
    ]


def vegetation_series(location_id: str, start_date: str, end_date: str) -> list[dict[str, Any]]:
    scenario = scenario_for_window(location_id, start_date, end_date)
    return [
        {
            "date": scenario.coverage_end.isoformat(),
            "ndvi": scenario.ndvi_current,
            "quality_flag": (
                "approved" if scenario.ndvi_quality_approved else "not_approved"
            ),
            "dataset_name": "modis_ndvi_demo",
            "dataset_version": "synthetic-v1",
        }
    ]


def historical_baseline(location_id: str, metric: str, window_definition: str) -> dict[str, Any]:
    _validate_location(location_id)
    if metric != "cumulative_rainfall" or window_definition != "45_day_post_planting":
        raise ValueError("Only the packaged 45-day cumulative-rainfall baseline is available")
    return {
        "location_id": location_id,
        "metric": metric,
        "window_definition": window_definition,
        "values_mm": fixture_document()["historical_45_day_rainfall_mm"],
        "dataset_version": "synthetic-v1",
    }


def data_provenance(dataset_name: str, dataset_version: str) -> dict[str, Any]:
    for item in load_provenance()["datasets"]:
        if item["dataset_name"] == dataset_name and item["dataset_version"] == dataset_version:
            return item
    raise ValueError("Dataset name or version is not allowlisted")

