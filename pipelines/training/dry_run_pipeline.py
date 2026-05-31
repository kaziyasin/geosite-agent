from __future__ import annotations

from pathlib import Path
from typing import Any

from training.reproducibility import collect_reproducibility_metadata

try:
    from zenml import pipeline, step
except ImportError:  # pragma: no cover - exercised only before ZenML install
    pipeline = None
    step = None


if step is not None:

    @step
    def collect_run_context_step(
        repo_root: str,
        dataset_manifest_path: str,
        prepared_metadata_path: str,
    ) -> dict[str, Any]:
        return collect_reproducibility_metadata(
            repo_root=Path(repo_root),
            dataset_manifest_path=Path(dataset_manifest_path),
            prepared_metadata_path=Path(prepared_metadata_path),
            include_installed_packages=True,
        )

    @step
    def create_training_plan_step(run_context: dict[str, Any]) -> dict[str, Any]:
        return {
            "status": "dry_run",
            "target_model_family": "rf-detr",
            "reproducibility_contract_version": run_context["reproducibility_contract_version"],
            "git_commit": run_context["git"]["commit"],
            "dataset_manifest_sha256": run_context["data_lineage"]["dataset_manifest"]["sha256"],
            "prepared_metadata_sha256": run_context["data_lineage"]["prepared_metadata"]["sha256"],
            "promotion_status": "not_evaluated",
        }


if pipeline is not None:

    @pipeline
    def detector_training_dry_run_pipeline(
        repo_root: str,
        dataset_manifest_path: str,
        prepared_metadata_path: str,
    ) -> dict[str, Any]:
        run_context = collect_run_context_step(
            repo_root=repo_root,
            dataset_manifest_path=dataset_manifest_path,
            prepared_metadata_path=prepared_metadata_path,
        )
        return create_training_plan_step(run_context)


def run_without_zenml(
    repo_root: Path,
    dataset_manifest_path: Path,
    prepared_metadata_path: Path,
) -> dict[str, Any]:
    run_context = collect_reproducibility_metadata(
        repo_root=repo_root,
        dataset_manifest_path=dataset_manifest_path,
        prepared_metadata_path=prepared_metadata_path,
        include_installed_packages=False,
    )
    return {
        "status": "dry_run",
        "target_model_family": "rf-detr",
        "reproducibility_contract_version": run_context["reproducibility_contract_version"],
        "git_commit": run_context["git"]["commit"],
        "dataset_manifest_sha256": run_context["data_lineage"]["dataset_manifest"]["sha256"],
        "prepared_metadata_sha256": run_context["data_lineage"]["prepared_metadata"]["sha256"],
        "promotion_status": "not_evaluated",
    }
