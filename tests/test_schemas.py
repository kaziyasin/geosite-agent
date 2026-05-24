from geosite_api.mock_data import demo_site_analysis
from geosite_schemas import SiteAnalysisResponse


def test_demo_payload_matches_schema() -> None:
    payload = demo_site_analysis()

    assert isinstance(payload, SiteAnalysisResponse)
    assert payload.sites
    assert payload.mlops_status.promotion_status == "mocked"


def test_demo_payload_serializes_to_expected_shape() -> None:
    payload = demo_site_analysis().model_dump()

    assert payload["sites"][0]["detections"][0]["label"] == "construction_site"
    assert payload["sites"][0]["evidence"][0]["source_type"] == "visual"
