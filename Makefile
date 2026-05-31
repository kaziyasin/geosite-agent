.PHONY: setup test dev-api dev-frontend compose-up compose-down compose-config

PYTHONPATH := services/api:services/agent:services/inference:packages/schemas:pipelines

setup:
	uv sync
	cd frontend && npm install

test:
	PYTHONPATH=$(PYTHONPATH) uv run pytest

dev-api:
	PYTHONPATH=$(PYTHONPATH) uv run uvicorn geosite_api.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd frontend && npm run dev

compose-up:
	docker compose -f infrastructure/docker/docker-compose.yml up --build

compose-down:
	docker compose -f infrastructure/docker/docker-compose.yml down

compose-config:
	docker compose -f infrastructure/docker/docker-compose.yml config
