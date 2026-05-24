# GeoSite Agent Architecture

GeoSite Agent is organized as a modular AI platform for real estate development analysis. The first milestone creates the skeleton; later milestones replace mocked data with real imagery, detections, retrieval, and agent execution.

## High-Level Flow

```text
Public satellite or aerial imagery
        ↓
Tiling and metadata extraction
        ↓
Versioned object storage
        ↓
Construction-site detection
        ↓
Embedding and indexing
        ↓
Agentic RAG workflow
        ↓
Analyst dashboard and review queue
```

## Core Services

- **API gateway**: FastAPI service exposing health, version, site, report, and review endpoints.
- **Agent worker**: future LangGraph service for planning, retrieval, tool execution, evidence validation, and structured reporting.
- **Inference service**: future RF-DETR service for tile-level construction-site detection.
- **Frontend**: Next.js dashboard for map exploration, detections, evidence, reports, and MLOps status.
- **Storage layer**: planned MinIO, lakeFS, Postgres, and pgvector.
- **MLOps layer**: planned ZenML and MLflow for retraining, tracking, registry, and promotion gates.

## Data Contracts

Milestone 1 uses shared Pydantic schemas for site-analysis responses. The same contracts are intended to support the frontend, tests, API, and future agent output validation.

## Deployment Shape

Milestone 1 includes Docker Compose for local development. Later milestones add kind and Helm so the services can run as a lightweight Kubernetes stack on macOS.
