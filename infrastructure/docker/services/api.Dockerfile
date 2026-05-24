FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml ./
COPY services/api ./services/api
COPY packages/schemas ./packages/schemas

RUN pip install --no-cache-dir fastapi "uvicorn[standard]" pydantic

ENV PYTHONPATH=/app/services/api:/app/packages/schemas

EXPOSE 8000

CMD ["uvicorn", "geosite_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
