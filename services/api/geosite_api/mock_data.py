from geosite_schemas import (
    AgentReport,
    Detection,
    EvidenceItem,
    MLOpsStatus,
    SiteAnalysisResponse,
    SiteSummary,
)


def demo_site_analysis() -> SiteAnalysisResponse:
    return SiteAnalysisResponse(
        query="Find likely construction activity in the demo region.",
        sites=[
            SiteSummary(
                site_id="site_demo_001",
                name="North Terrace mixed-use parcel",
                priority="high",
                latitude=-34.9212,
                longitude=138.5995,
                detections=[
                    Detection(
                        detection_id="det_001",
                        label="construction_site",
                        confidence=0.86,
                        bbox_xyxy=(118, 94, 338, 286),
                        model_version="rfdetr-nano-mock-v0",
                    )
                ],
                evidence=[
                    EvidenceItem(
                        evidence_id="ev_visual_001",
                        source_type="visual",
                        title="Likely active construction footprint",
                        summary="The mocked detector found a rectangular disturbed area consistent with early development activity.",
                        confidence=0.86,
                    ),
                    EvidenceItem(
                        evidence_id="ev_metric_001",
                        source_type="metric",
                        title="Commercial proximity score",
                        summary="The site is close to transport and dense commercial land-use signals in the demo metadata.",
                        confidence=0.74,
                    ),
                ],
                agent_report=AgentReport(
                    summary="One high-priority site is ready for analyst review.",
                    recommendation="Review the site before adding it to the retraining feedback set.",
                    business_confidence=0.78,
                    requires_human_review=True,
                    reasoning_trace=[
                        "Classified request as site discovery.",
                        "Retrieved mocked visual detection evidence.",
                        "Combined detection confidence with commercial proximity metadata.",
                        "Routed to human review because this is a mocked milestone response.",
                    ],
                ),
            )
        ],
        mlops_status=MLOpsStatus(
            dataset_version="mock-dataset-v0",
            model_version="rfdetr-nano-mock-v0",
            last_eval_score=0.0,
            promotion_status="mocked",
        ),
    )
