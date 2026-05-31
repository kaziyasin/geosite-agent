# MLOps

GeoSite Agent treats reproducibility as a training prerequisite. No detector training run should start unless the pipeline can record the exact code, data, dependencies, hardware, and training configuration used to produce the model.

## Locked Decisions

- **Pipeline orchestrator**: ZenML.
- **Experiment tracker**: MLflow.
- **Current execution mode**: local.
- **Future data versioning**: lakeFS over object storage.
- **Python target**: 3.13, because the MLOps stack must avoid unsupported Python versions.

## Reproducibility Contract

Every training run must capture:

- Git commit, branch, remote, and dirty-state flag.
- Python version, executable, and `.python-version` hash.
- `pyproject.toml` and `uv.lock` hashes.
- Installed package snapshot for real training runs.
- OS, CPU, memory, and available accelerators such as MPS/CUDA.
- Dataset manifest hash and prepared dataset metadata hash.
- Future lakeFS repo, branch, commit, and tag.
- Training config hash, hyperparameters, seeds, and promotion status.
- MLflow run id and ZenML pipeline/step metadata once real training is wired in.

The local metadata command is:

```bash
make repro-metadata
```

This writes a local ignored artifact:

```text
data/manifests/repro_metadata.local.json
```

## Local ZenML/MLflow Setup

Install project dependencies with:

```bash
uv sync
```

For Apple Silicon local ZenML server/dashboard workflows, set this when needed:

```bash
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
```

The first ZenML pipeline is a dry-run detector training pipeline. Its purpose is to prove that run context and lineage are captured before RF-DETR training is added.

## Promotion Rule

A model cannot be promoted unless:

- the training run has complete reproducibility metadata,
- the dataset has a manifest,
- the prepared dataset metadata is present,
- the Git working tree state is recorded,
- evaluation metrics exist in MLflow,
- the future lakeFS data version is attached once lakeFS is enabled.
