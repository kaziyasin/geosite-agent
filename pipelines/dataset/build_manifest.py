from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from dataset.inspect_coco import CocoDatasetSummary, inspect_coco_dataset

DEFAULT_SPLITS = ("train", "valid", "test")


@dataclass(frozen=True)
class DatasetManifestConfig:
    dataset_name: str
    dataset_root: Path
    output_file: Path
    splits: tuple[str, ...] = DEFAULT_SPLITS
    dataset_role: str = "poc"
    annotation_format: str = "coco"
    target_model_family: str = "rf-detr"
    provider: str = "roboflow"
    license_name: str = "to_verify"
    current_version_mode: str = "local_only"
    future_version_system: str = "lakefs"
    lakefs_repo: str = "geosite-agent"


def build_dataset_manifest(config: DatasetManifestConfig) -> dict[str, Any]:
    dataset_root = config.dataset_root.expanduser().resolve()
    split_summaries = {
        split: _inspect_split(dataset_root, split).to_dict()
        for split in config.splits
    }
    raw_categories = sorted(
        {
            category
            for summary in split_summaries.values()
            for category in summary["categories"]
        }
    )

    return {
        "dataset_name": config.dataset_name,
        "dataset_role": config.dataset_role,
        "annotation_format": config.annotation_format,
        "target_model_family": config.target_model_family,
        "generated_at": datetime.now(UTC).isoformat(),
        "source": {
            "provider": config.provider,
            "local_path": str(config.dataset_root),
            "license": config.license_name,
        },
        "versioning": {
            "current_mode": config.current_version_mode,
            "future_system": config.future_version_system,
            "lakefs_repo": config.lakefs_repo,
            "lakefs_branch": None,
            "lakefs_commit": None,
            "lakefs_tag": None,
        },
        "splits": split_summaries,
        "class_policy": {
            "raw_categories": raw_categories,
            "ignored_categories": _suggest_ignored_categories(raw_categories),
            "target_categories": _suggest_target_categories(raw_categories),
        },
    }


def write_dataset_manifest(config: DatasetManifestConfig) -> dict[str, Any]:
    manifest = build_dataset_manifest(config)
    output_file = config.output_file.expanduser().resolve()
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def _inspect_split(dataset_root: Path, split: str) -> CocoDatasetSummary:
    split_root = dataset_root / split
    return inspect_coco_dataset(
        annotation_file=split_root / "_annotations.coco.json",
        image_root=split_root,
    )


def _suggest_ignored_categories(categories: list[str]) -> list[str]:
    return [
        category
        for category in categories
        if "object-detection" in category or "photographs" in category or len(category) > 80
    ]


def _suggest_target_categories(categories: list[str]) -> list[str]:
    ignored = set(_suggest_ignored_categories(categories))
    return [category for category in categories if category not in ignored]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a dataset manifest from COCO splits.")
    parser.add_argument("--dataset-name", required=True, help="Stable dataset name.")
    parser.add_argument("--dataset-root", required=True, type=Path, help="Dataset root containing split folders.")
    parser.add_argument("--output", required=True, type=Path, help="Manifest output JSON path.")
    parser.add_argument("--provider", default="roboflow", help="Dataset provider name.")
    parser.add_argument("--license", default="to_verify", help="Dataset license status/name.")
    parser.add_argument(
        "--splits",
        nargs="+",
        default=list(DEFAULT_SPLITS),
        help="Split names to inspect. Defaults to train valid test.",
    )
    args = parser.parse_args()

    manifest = write_dataset_manifest(
        DatasetManifestConfig(
            dataset_name=args.dataset_name,
            dataset_root=args.dataset_root,
            output_file=args.output,
            splits=tuple(args.splits),
            provider=args.provider,
            license_name=args.license,
        )
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
