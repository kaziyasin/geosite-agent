# GeoSite Agent

GeoSite Agent is an agentic RAG platform for real estate development analysis from satellite and aerial imagery. The project is designed as a Staff/Senior AI engineering portfolio system: computer vision provides visual evidence, retrieval grounds the context, and an agentic workflow turns both into reviewable site recommendations.

## Business Problem

Real estate analysts need to monitor large regions for development activity, commercial expansion, and construction signals. Manual review of satellite imagery is slow, inconsistent, and difficult to connect with zoning notes, market reports, and prior analyst decisions.

GeoSite Agent is built to answer questions like:

> Which locations show likely construction activity, and which sites should an analyst review next?

## Architecture

```text
Satellite imagery + business documents
        ↓
Data ingestion and tiling
        ↓
Versioned data lake
        ↓
RF-DETR detection pipeline
        ↓
Postgres + pgvector retrieval layer
        ↓
LangGraph agent workflow
        ↓
FastAPI + Next.js dashboard
        ↓
MLflow, ZenML, CI/CD, and Kubernetes deployment
```

Milestone 1 provides the runnable skeleton: API health checks, mocked site-analysis responses, agent and inference placeholders, dashboard shell, docs, and tests.

## Tech Stack

- **FastAPI** for the API gateway because it is widely used for production AI services and easy to test.
- **Next.js + React** for a professional dashboard surface.
- **RF-DETR Nano** as the planned first detector for construction-site signals.
- **LangGraph** as the planned agent orchestration layer for explicit state, tools, routing, and traces.
- **Postgres + pgvector** as the planned vector store because it keeps SQL metadata and vector search in one open-source database.
- **lakeFS + MinIO** as the planned data-versioning layer.
- **ZenML + MLflow** as the planned MLOps stack for pipelines, experiment tracking, model registry, and promotion gates.
- **kind + Helm** as the planned local Kubernetes deployment path.

## Quickstart

Install the project dependencies:

```bash
make setup
```

Run the API:

```bash
make dev-api
```

Run the frontend:

```bash
make dev-frontend
```

Run tests:

```bash
make test
```

Start the local Docker Compose profile:

```bash
make compose-up
```

> Note: this workspace currently expects `uv`, `npm`, and Docker to be installed by the developer. The scaffold is ready for those tools, but they may not exist on a fresh macOS shell.

## Current API Surface

- `GET /health` returns service health.
- `GET /version` returns project and service version metadata.
- `GET /sites/demo` returns mocked site-analysis data shaped like the future agent output.

## Roadmap

1. **Milestone 1: Project Skeleton**
   - FastAPI health/version/demo endpoints.
   - Dashboard shell with mocked site data.
   - Shared schemas, docs, tests, and Docker Compose.
2. **Milestone 2: Dataset + Tiling**
   - Public imagery sample, tile manifests, annotation conversion, and lakeFS layout.
3. **Milestone 3: CV Inference**
   - RF-DETR Nano inference service and detection overlays.
4. **Milestone 4: Vector + RAG Layer**
   - Postgres + pgvector indexing for tiles, detections, and documents.
5. **Milestone 5: Agentic Workflow**
   - LangGraph tools for retrieval, site scoring, reporting, and human review routing.
6. **Milestone 6: MLOps**
   - ZenML retraining pipeline, MLflow tracking, registry, and promotion gates.
7. **Milestone 7: Kubernetes**
   - kind cluster, Helm charts, GitHub Actions smoke deployment.
8. **Milestone 8: Portfolio Polish**
   - Screenshots, demo GIF, evaluation results, and failure-mode documentation.

## Documentation

- [Architecture](docs/architecture.md)
- [Dataset pipeline](docs/dataset.md)
- [API service](services/api/README.md)
- [Agent service](services/agent/README.md)
- [Inference service](services/inference/README.md)
- [Frontend](frontend/README.md)
