from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DEFAULT_SPLITS = ("train", "valid", "test")


class CocoPreparationError(ValueError):
    """Raised when a COCO dataset cannot be prepared."""


@dataclass(frozen=True)
class CocoPreparationConfig:
    manifest_file: Path
    raw_dataset_root: Path
    output_root: Path
    splits: tuple[str, ...] = DEFAULT_SPLITS
    copy_images: bool = True


def prepare_coco_dataset(config: CocoPreparationConfig) -> dict[str, Any]:
    manifest = _load_json(config.manifest_file)
    target_categories = manifest.get("class_policy", {}).get("target_categories")
    ignored_categories = manifest.get("class_policy", {}).get("ignored_categories", [])

    if not isinstance(target_categories, list) or not target_categories:
        raise CocoPreparationError("Manifest must include class_policy.target_categories.")
    if not all(isinstance(category, str) and category for category in target_categories):
        raise CocoPreparationError("Target categories must be non-empty strings.")
    if not isinstance(ignored_categories, list):
        raise CocoPreparationError("Ignored categories must be a list.")

    output_root = config.output_root.expanduser().resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    category_name_to_new_id = {
        category_name: index
        for index, category_name in enumerate(target_categories, start=1)
    }

    split_results = {
        split: _prepare_split(
            split=split,
            raw_dataset_root=config.raw_dataset_root.expanduser().resolve(),
            output_root=output_root,
            category_name_to_new_id=category_name_to_new_id,
            ignored_categories=set(ignored_categories),
            copy_images=config.copy_images,
        )
        for split in config.splits
    }

    preparation_metadata = {
        "prepared_at": datetime.now(UTC).isoformat(),
        "source_manifest": str(config.manifest_file),
        "raw_dataset_root": str(config.raw_dataset_root),
        "output_root": str(config.output_root),
        "copy_images": config.copy_images,
        "versioning": {
            "current_mode": "local_only",
            "future_system": "lakefs",
            "lakefs_repo": manifest.get("versioning", {}).get("lakefs_repo", "geosite-agent"),
            "lakefs_branch": None,
            "lakefs_commit": None,
            "lakefs_tag": None,
        },
        "class_mapping": [
            {"id": category_id, "name": category_name}
            for category_name, category_id in category_name_to_new_id.items()
        ],
        "ignored_categories": ignored_categories,
        "splits": split_results,
    }

    (output_root / "preparation_metadata.local.json").write_text(
        json.dumps(preparation_metadata, indent=2) + "\n",
        encoding="utf-8",
    )
    return preparation_metadata


def _prepare_split(
    split: str,
    raw_dataset_root: Path,
    output_root: Path,
    category_name_to_new_id: dict[str, int],
    ignored_categories: set[str],
    copy_images: bool,
) -> dict[str, Any]:
    raw_split_root = raw_dataset_root / split
    output_split_root = output_root / split
    output_split_root.mkdir(parents=True, exist_ok=True)

    source_annotations = _load_json(raw_split_root / "_annotations.coco.json")
    source_categories = _require_list(source_annotations, "categories")
    source_images = _require_list(source_annotations, "images")
    source_annotations_list = _require_list(source_annotations, "annotations")

    old_category_id_to_name = {
        _require_int(category, "id"): _require_str(category, "name")
        for category in source_categories
    }
    old_category_id_to_new_id = {
        old_id: category_name_to_new_id[name]
        for old_id, name in old_category_id_to_name.items()
        if name in category_name_to_new_id
    }
    ignored_old_category_ids = {
        old_id
        for old_id, name in old_category_id_to_name.items()
        if name in ignored_categories
    }

    images_by_id = {
        _require_int(image, "id"): image
        for image in source_images
    }
    kept_image_ids: set[int] = set()
    cleaned_annotations: list[dict[str, Any]] = []
    dropped_annotation_count = 0

    for source_annotation in source_annotations_list:
        old_category_id = _require_int(source_annotation, "category_id")
        old_image_id = _require_int(source_annotation, "image_id")

        if old_category_id in ignored_old_category_ids:
            dropped_annotation_count += 1
            continue
        if old_category_id not in old_category_id_to_new_id:
            dropped_annotation_count += 1
            continue
        if old_image_id not in images_by_id:
            raise CocoPreparationError(f"Annotation references missing image_id {old_image_id}.")

        cleaned_annotation = dict(source_annotation)
        cleaned_annotation["id"] = len(cleaned_annotations) + 1
        cleaned_annotation["category_id"] = old_category_id_to_new_id[old_category_id]
        cleaned_annotations.append(cleaned_annotation)
        kept_image_ids.add(old_image_id)

    cleaned_images = [
        dict(image)
        for image in source_images
        if _require_int(image, "id") in kept_image_ids
    ]

    if copy_images:
        for image in cleaned_images:
            file_name = _require_str(image, "file_name")
            source_image = raw_split_root / file_name
            destination_image = output_split_root / file_name
            if not source_image.is_file():
                raise CocoPreparationError(f"Image file does not exist: {source_image}")
            if not destination_image.exists():
                shutil.copy2(source_image, destination_image)

    cleaned_categories = [
        {"id": category_id, "name": category_name}
        for category_name, category_id in category_name_to_new_id.items()
    ]
    cleaned_payload = {
        "images": cleaned_images,
        "annotations": cleaned_annotations,
        "categories": cleaned_categories,
    }
    (output_split_root / "_annotations.coco.json").write_text(
        json.dumps(cleaned_payload, indent=2) + "\n",
        encoding="utf-8",
    )

    return {
        "image_count": len(cleaned_images),
        "annotation_count": len(cleaned_annotations),
        "dropped_annotation_count": dropped_annotation_count,
        "category_count": len(cleaned_categories),
        "annotation_file": str(output_split_root / "_annotations.coco.json"),
    }


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise CocoPreparationError(f"JSON file does not exist: {path}")
    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except json.JSONDecodeError as exc:
        raise CocoPreparationError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise CocoPreparationError(f"JSON file must contain an object: {path}")
    return payload


def _require_list(payload: dict[str, Any], key: str) -> list[Any]:
    value = payload.get(key)
    if not isinstance(value, list):
        raise CocoPreparationError(f"Expected list field '{key}'.")
    return value


def _require_int(payload: Any, key: str) -> int:
    if not isinstance(payload, dict) or not isinstance(payload.get(key), int):
        raise CocoPreparationError(f"Expected integer field '{key}'.")
    return payload[key]


def _require_str(payload: Any, key: str) -> str:
    if not isinstance(payload, dict) or not isinstance(payload.get(key), str) or not payload[key]:
        raise CocoPreparationError(f"Expected non-empty string field '{key}'.")
    return payload[key]


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare a clean COCO dataset from a manifest.")
    parser.add_argument("--manifest", required=True, type=Path, help="Dataset manifest JSON path.")
    parser.add_argument("--raw-root", required=True, type=Path, help="Raw dataset root containing split folders.")
    parser.add_argument("--output-root", required=True, type=Path, help="Prepared dataset output root.")
    parser.add_argument(
        "--splits",
        nargs="+",
        default=list(DEFAULT_SPLITS),
        help="Split names to prepare. Defaults to train valid test.",
    )
    parser.add_argument(
        "--no-copy-images",
        action="store_true",
        help="Write cleaned annotations without copying image files.",
    )
    args = parser.parse_args()

    metadata = prepare_coco_dataset(
        CocoPreparationConfig(
            manifest_file=args.manifest,
            raw_dataset_root=args.raw_root,
            output_root=args.output_root,
            splits=tuple(args.splits),
            copy_images=not args.no_copy_images,
        )
    )
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
