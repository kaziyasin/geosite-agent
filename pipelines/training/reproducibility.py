from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

TRACKED_ENV_VARS = (
    "CUDA_VISIBLE_DEVICES",
    "MLFLOW_TRACKING_URI",
    "OBJC_DISABLE_INITIALIZE_FORK_SAFETY",
    "PYTHONHASHSEED",
    "PYTORCH_ENABLE_MPS_FALLBACK",
    "ZENML_ACTIVE_STACK_ID",
    "ZENML_ANALYTICS_OPT_IN",
)


def collect_reproducibility_metadata(
    repo_root: Path,
    dataset_manifest_path: Path | None = None,
    prepared_metadata_path: Path | None = None,
    training_config_path: Path | None = None,
    include_installed_packages: bool = False,
) -> dict[str, Any]:
    repo_root = repo_root.expanduser().resolve()
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "reproducibility_contract_version": "1.0",
        "git": _git_metadata(repo_root),
        "python": _python_metadata(),
        "system": _system_metadata(),
        "hardware": _hardware_metadata(),
        "dependencies": _dependency_metadata(repo_root, include_installed_packages),
        "environment": _environment_metadata(),
        "data_lineage": _data_lineage_metadata(
            dataset_manifest_path=dataset_manifest_path,
            prepared_metadata_path=prepared_metadata_path,
        ),
        "training_config": _file_reference(training_config_path),
        "mlops": {
            "orchestrator": "zenml",
            "experiment_tracker": "mlflow",
            "data_versioning": "lakefs_planned",
            "model_registry": "mlflow_planned",
            "required_before_training": True,
        },
    }


def write_reproducibility_metadata(
    output_path: Path,
    metadata: dict[str, Any],
) -> None:
    output_path = output_path.expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")


def _git_metadata(repo_root: Path) -> dict[str, Any]:
    return {
        "commit": _run_git(repo_root, "rev-parse", "HEAD"),
        "branch": _run_git(repo_root, "branch", "--show-current"),
        "remote_origin": _run_git(repo_root, "remote", "get-url", "origin"),
        "is_dirty": bool(_run_git(repo_root, "status", "--porcelain")),
    }


def _python_metadata() -> dict[str, Any]:
    return {
        "version": platform.python_version(),
        "implementation": platform.python_implementation(),
        "executable": sys.executable,
        "major": sys.version_info.major,
        "minor": sys.version_info.minor,
        "micro": sys.version_info.micro,
    }


def _system_metadata() -> dict[str, Any]:
    return {
        "platform": platform.platform(),
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
    }


def _hardware_metadata() -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "cpu_count": os.cpu_count(),
        "macos_sysctl": {},
        "accelerators": {
            "torch_available": False,
            "mps_available": None,
            "cuda_available": None,
        },
    }
    if platform.system() == "Darwin":
        metadata["macos_sysctl"] = {
            "cpu_brand": _sysctl("machdep.cpu.brand_string"),
            "logical_cpu": _sysctl("hw.logicalcpu"),
            "physical_cpu": _sysctl("hw.physicalcpu"),
            "memory_bytes": _sysctl("hw.memsize"),
            "machine": _sysctl("hw.machine"),
        }

    try:
        import torch  # type: ignore[import-not-found]
    except Exception:
        return metadata

    metadata["accelerators"] = {
        "torch_available": True,
        "torch_version": getattr(torch, "__version__", None),
        "mps_available": bool(getattr(torch.backends, "mps", None) and torch.backends.mps.is_available()),
        "cuda_available": bool(torch.cuda.is_available()),
        "cuda_device_count": int(torch.cuda.device_count()),
    }
    return metadata


def _dependency_metadata(repo_root: Path, include_installed_packages: bool) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "pyproject": _file_reference(repo_root / "pyproject.toml"),
        "uv_lock": _file_reference(repo_root / "uv.lock"),
        "python_version_file": _file_reference(repo_root / ".python-version"),
        "installed_packages": None,
    }
    if include_installed_packages:
        metadata["installed_packages"] = _run_command(repo_root, "uv", "pip", "freeze").splitlines()
    return metadata


def _environment_metadata() -> dict[str, Any]:
    return {
        name: os.environ.get(name)
        for name in TRACKED_ENV_VARS
    }


def _data_lineage_metadata(
    dataset_manifest_path: Path | None,
    prepared_metadata_path: Path | None,
) -> dict[str, Any]:
    dataset_manifest = _file_reference(dataset_manifest_path)
    prepared_metadata = _file_reference(prepared_metadata_path)
    lineage: dict[str, Any] = {
        "dataset_manifest": dataset_manifest,
        "prepared_metadata": prepared_metadata,
        "lakefs": {
            "repo": None,
            "branch": None,
            "commit": None,
            "tag": None,
        },
    }

    manifest_payload = _read_json_if_present(dataset_manifest_path)
    if manifest_payload:
        versioning = manifest_payload.get("versioning", {})
        lineage["lakefs"] = {
            "repo": versioning.get("lakefs_repo"),
            "branch": versioning.get("lakefs_branch"),
            "commit": versioning.get("lakefs_commit"),
            "tag": versioning.get("lakefs_tag"),
        }
    return lineage


def _file_reference(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    resolved = path.expanduser().resolve()
    if not resolved.is_file():
        return {
            "path": str(path),
            "exists": False,
            "sha256": None,
        }
    return {
        "path": str(path),
        "exists": True,
        "sha256": _sha256(resolved),
        "size_bytes": resolved.stat().st_size,
    }


def _read_json_if_present(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    resolved = path.expanduser().resolve()
    if not resolved.is_file():
        return None
    with resolved.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload if isinstance(payload, dict) else None


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sysctl(key: str) -> str | None:
    value = _run_command(Path.cwd(), "sysctl", "-n", key)
    return value or None


def _run_git(repo_root: Path, *args: str) -> str | None:
    return _run_command(repo_root, "git", *args) or None


def _run_command(cwd: Path, *args: str) -> str:
    try:
        result = subprocess.run(
            args,
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return ""
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect training reproducibility metadata.")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repository root.")
    parser.add_argument("--dataset-manifest", type=Path, help="Dataset manifest JSON path.")
    parser.add_argument("--prepared-metadata", type=Path, help="Prepared dataset metadata JSON path.")
    parser.add_argument("--training-config", type=Path, help="Training config file path.")
    parser.add_argument("--output", type=Path, help="Output JSON path.")
    parser.add_argument("--include-installed-packages", action="store_true")
    parser.add_argument("--json", action="store_true", help="Print metadata JSON.")
    args = parser.parse_args()

    metadata = collect_reproducibility_metadata(
        repo_root=args.repo_root,
        dataset_manifest_path=args.dataset_manifest,
        prepared_metadata_path=args.prepared_metadata,
        training_config_path=args.training_config,
        include_installed_packages=args.include_installed_packages,
    )
    if args.output:
        write_reproducibility_metadata(args.output, metadata)
    if args.json or not args.output:
        print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
