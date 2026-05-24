# API Service

FastAPI gateway for GeoSite Agent.

## Current Endpoints

- `GET /health`
- `GET /version`
- `GET /sites/demo`

## Run

```bash
make dev-api
```

The milestone 1 service returns mocked site-analysis data. Later milestones will connect it to retrieval, agent execution, inference, review workflows, and MLOps metadata.
