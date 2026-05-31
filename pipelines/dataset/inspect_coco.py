from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class CocoInspectionError(ValueError):
    """Raised when a COCO dataset fails validation."""


@dataclass(frozen=True)
class CocoDatasetSummary:
    annotation_file: Path
    image_root: Path
    image_count: int
    annotation_count: int
    category_count: int
    missing_image_count: int
    empty_image_count: int
    categories: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "annotation_file": str(self.annotation_file),
            "image_root": str(self.image_root),
            "image_count": self.image_count,
            "annotation_count": self.annotation_count,
            "category_count": self.category_count,
            "missing_image_count": self.missing_image_count,
            "empty_image_count": self.empty_image_count,
            "categories": list(self.categories),
        }


def inspect_coco_dataset(annotation_file: Path, image_root: Path) -> CocoDatasetSummary:
    annotation_file = annotation_file.expanduser().resolve()
    image_root = image_root.expanduser().resolve()

    if not annotation_file.is_file():
        raise CocoInspectionError(f"COCO annotation file does not exist: {annotation_file}")
    if not image_root.is_dir():
        raise CocoInspectionError(f"Image root does not exist: {image_root}")

    payload = _load_json(annotation_file)
    images = _require_list(payload, "images")
    annotations = _require_list(payload, "annotations")
    categories = _require_list(payload, "categories")

    if not images:
        raise CocoInspectionError("COCO file has no images.")
    if not categories:
        raise CocoInspectionError("COCO file has no categories.")

    image_ids: set[int] = set()
    category_ids: set[int] = set()
    category_names: list[str] = []
    missing_images: list[str] = []
    image_annotation_counts: dict[int, int] = {}

    for category in categories:
        category_id = _require_int(category, "id", "category")
        category_name = _require_str(category, "name", "category")
        category_ids.add(category_id)
        category_names.append(category_name)

    for image in images:
        image_id = _require_int(image, "id", "image")
        file_name = _require_str(image, "file_name", "image")
        width = _require_number(image, "width", "image")
        height = _require_number(image, "height", "image")

        if image_id in image_ids:
            raise CocoInspectionError(f"Duplicate image id: {image_id}")
        if width <= 0 or height <= 0:
            raise CocoInspectionError(f"Image {image_id} has invalid dimensions: {width}x{height}")

        image_ids.add(image_id)
        image_annotation_counts[image_id] = 0
        if not (image_root / file_name).is_file():
            missing_images.append(file_name)

    for annotation in annotations:
        annotation_id = _require_int(annotation, "id", "annotation")
        image_id = _require_int(annotation, "image_id", f"annotation {annotation_id}")
        category_id = _require_int(annotation, "category_id", f"annotation {annotation_id}")
        bbox = annotation.get("bbox")

        if image_id not in image_ids:
            raise CocoInspectionError(f"Annotation {annotation_id} references missing image_id {image_id}")
        if category_id not in category_ids:
            raise CocoInspectionError(
                f"Annotation {annotation_id} references missing category_id {category_id}"
            )
        _validate_bbox(bbox, annotation_id)
        image_annotation_counts[image_id] += 1

    empty_image_count = sum(1 for count in image_annotation_counts.values() if count == 0)

    return CocoDatasetSummary(
        annotation_file=annotation_file,
        image_root=image_root,
        image_count=len(images),
        annotation_count=len(annotations),
        category_count=len(categories),
        missing_image_count=len(missing_images),
        empty_image_count=empty_image_count,
        categories=tuple(sorted(category_names)),
    )


def _load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except json.JSONDecodeError as exc:
        raise CocoInspectionError(f"Invalid JSON in {path}: {exc}") from exc

    if not isinstance(payload, dict):
        raise CocoInspectionError("COCO file must contain a JSON object.")
    return payload


def _require_list(payload: dict[str, Any], key: str) -> list[Any]:
    value = payload.get(key)
    if not isinstance(value, list):
        raise CocoInspectionError(f"COCO field '{key}' must be a list.")
    return value


def _require_int(payload: Any, key: str, context: str) -> int:
    if not isinstance(payload, dict) or not isinstance(payload.get(key), int):
        raise CocoInspectionError(f"{context} must include integer field '{key}'.")
    return payload[key]


def _require_str(payload: Any, key: str, context: str) -> str:
    if not isinstance(payload, dict) or not isinstance(payload.get(key), str) or not payload[key]:
        raise CocoInspectionError(f"{context} must include non-empty string field '{key}'.")
    return payload[key]


def _require_number(payload: Any, key: str, context: str) -> float:
    if not isinstance(payload, dict) or not isinstance(payload.get(key), int | float):
        raise CocoInspectionError(f"{context} must include numeric field '{key}'.")
    return float(payload[key])


def _validate_bbox(bbox: Any, annotation_id: int) -> None:
    if not isinstance(bbox, list) or len(bbox) != 4:
        raise CocoInspectionError(f"Annotation {annotation_id} must include bbox [x, y, width, height].")

    if not all(isinstance(value, int | float) for value in bbox):
        raise CocoInspectionError(f"Annotation {annotation_id} bbox values must be numeric.")

    _, _, width, height = bbox
    if width <= 0 or height <= 0:
        raise CocoInspectionError(f"Annotation {annotation_id} bbox width and height must be positive.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect a COCO object detection dataset.")
    parser.add_argument("--annotations", required=True, type=Path, help="Path to COCO JSON annotations.")
    parser.add_argument("--images", required=True, type=Path, help="Directory containing image files.")
    parser.add_argument("--json", action="store_true", help="Print summary as JSON.")
    args = parser.parse_args()

    summary = inspect_coco_dataset(args.annotations, args.images)
    if args.json:
        print(json.dumps(summary.to_dict(), indent=2))
        return

    print(f"Annotation file: {summary.annotation_file}")
    print(f"Image root: {summary.image_root}")
    print(f"Images: {summary.image_count}")
    print(f"Annotations: {summary.annotation_count}")
    print(f"Categories: {summary.category_count} ({', '.join(summary.categories)})")
    print(f"Missing image files: {summary.missing_image_count}")
    print(f"Images without annotations: {summary.empty_image_count}")


if __name__ == "__main__":
    main()
