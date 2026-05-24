from fastapi import FastAPI

from geosite_api import __version__
from geosite_api.mock_data import demo_site_analysis
from geosite_schemas import HealthResponse, SiteAnalysisResponse, VersionResponse

app = FastAPI(
    title="GeoSite Agent API",
    version=__version__,
    description="API gateway for real estate development analysis workflows.",
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="api")


@app.get("/version", response_model=VersionResponse)
def version() -> VersionResponse:
    return VersionResponse(
        project="geosite-agent",
        service="api",
        version=__version__,
        milestone="1-project-skeleton",
    )


@app.get("/sites/demo", response_model=SiteAnalysisResponse)
def sites_demo() -> SiteAnalysisResponse:
    return demo_site_analysis()
