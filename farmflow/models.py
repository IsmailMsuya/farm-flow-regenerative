from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class DecisionStatus(StrEnum):
    NORMAL = "normal"
    WATCHLIST = "watchlist"
    TRIGGERED_REVIEW = "triggered_review"
    INSUFFICIENT_DATA = "insufficient_data"


class ReviewOutcome(StrEnum):
    REVIEW_PENDING = "review_pending"
    APPROVED_FOR_FOLLOW_UP = "approved_for_follow_up"
    MANUAL_REVIEW_REQUIRED = "manual_review_required"
    DECLINED_DUE_TO_INSUFFICIENT_EVIDENCE = "declined_due_to_insufficient_evidence"


class RainfallRule(BaseModel):
    metric: Literal["cumulative_rainfall"]
    comparator: Literal["below_historical_percentile"]
    percentile: float = Field(ge=0, le=100)


class VegetationRule(BaseModel):
    metric: Literal["ndvi_anomaly"]
    comparator: Literal["below_threshold"]
    threshold: float = Field(ge=-1, le=1)


class DataQualityRule(BaseModel):
    minimum_rainfall_coverage_percent: float = Field(ge=0, le=100)
    require_quality_approved_ndvi: bool


class ReliefOption(BaseModel):
    type: Literal["repayment_deferral"]
    duration_days: int = Field(gt=0, le=365)


class TransitionContract(BaseModel):
    model_config = ConfigDict(frozen=True)

    contract_id: str
    version: str
    crop: str
    coverage_window_days: int = Field(gt=0)
    rainfall_trigger: RainfallRule
    vegetation_confirmation: VegetationRule
    data_quality: DataQualityRule
    relief_option: ReliefOption
    mode: Literal["simulation_only"]


class Scenario(BaseModel):
    contract_id: str
    farmer_alias: str
    location_id: str
    coverage_start: date
    coverage_end: date
    rainfall_daily_mm: list[float | None]
    ndvi_current: float | None = Field(default=None, ge=-1, le=1)
    ndvi_baseline: float = Field(ge=-1, le=1)
    ndvi_quality_approved: bool | None = None


class RainfallAssessment(BaseModel):
    cumulative_rainfall_mm: float = Field(ge=0)
    historical_threshold_mm: float = Field(ge=0)
    rainfall_percentile: float = Field(ge=0, le=100)
    rainfall_coverage_percent: float = Field(ge=0, le=100)
    trigger_met: bool


class VegetationAssessment(BaseModel):
    ndvi_anomaly: float | None
    ndvi_quality_approved: bool | None
    confirmation_met: bool


class ClimateAssessment(BaseModel):
    assessment_id: str
    contract_id: str
    rule_contract_id: str
    cumulative_rainfall_mm: float
    historical_threshold_mm: float
    rainfall_percentile: float
    rainfall_coverage_percent: float
    ndvi_anomaly: float | None
    ndvi_quality_approved: bool | None
    status: DecisionStatus
    confidence: Literal["high", "medium", "low"]
    limitations: list[str]


class PolicyGateResult(BaseModel):
    allowed: bool
    reason: str
    blocked_categories: list[str] = Field(default_factory=list)


class AuditEvent(BaseModel):
    event_id: str
    timestamp: datetime
    agent_name: str
    tool_name: str
    policy_result: Literal["allowed", "blocked"]
    output_artifact_id: str


class ReviewPacket(BaseModel):
    packet_id: str
    contract_id: str
    assessment_id: str
    status: DecisionStatus
    recommended_next_step: str
    farmer_explanation: str
    reviewer_summary: str
    requires_human_review: Literal[True] = True
    policy_gate_result: PolicyGateResult
    audit_events: list[AuditEvent]
    disclaimer: str


UiComponentType = Literal[
    "status_card",
    "metric_card",
    "line_chart",
    "timeline",
    "evidence_list",
    "warning_banner",
    "review_action_panel",
]


class UiComponent(BaseModel):
    type: UiComponentType
    title: str
    data: dict[str, Any]


class UiSchema(BaseModel):
    version: Literal["1.0"] = "1.0"
    components: list[UiComponent]


class AssessmentResponse(BaseModel):
    scenario: Scenario
    assessment: ClimateAssessment
    packet: ReviewPacket
    ui: UiSchema

