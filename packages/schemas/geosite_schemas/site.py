from typing import Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str


class VersionResponse(BaseModel):
    project: str
    service: str
    version: str
    milestone: str


class Detection(BaseModel):
    detection_id: str
    label: str
    confidence: float = Field(ge=0.0, le=1.0)
    bbox_xyxy: tuple[int, int, int, int]
    model_version: str


class EvidenceItem(BaseModel):
    evidence_id: str
    source_type: Literal["visual", "document", "metric"]
    title: str
    summary: str
    confidence: float = Field(ge=0.0, le=1.0)


class AgentReport(BaseModel):
    summary: str
    recommendation: str
    business_confidence: float = Field(ge=0.0, le=1.0)
    requires_human_review: bool
    reasoning_trace: list[str]


class MLOpsStatus(BaseModel):
    dataset_version: str
    model_version: str
    last_eval_score: float = Field(ge=0.0, le=1.0)
    promotion_status: Literal["mocked", "candidate", "approved", "rejected"]


class SiteSummary(BaseModel):
    site_id: str
    name: str
    priority: Literal["low", "medium", "high"]
    latitude: float
    longitude: float
    detections: list[Detection]
    evidence: list[EvidenceItem]
    agent_report: AgentReport


class SiteAnalysisResponse(BaseModel):
    query: str
    sites: list[SiteSummary]
    mlops_status: MLOpsStatus
