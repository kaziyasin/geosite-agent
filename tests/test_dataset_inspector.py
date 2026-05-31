import json
from pathlib import Path

import pytest

from dataset.inspect_coco import CocoInspectionError, inspect_coco_dataset


def test_inspect_valid_coco_dataset(tmp_path: Path) -> None:
    image_root = tmp_path / "images"
    image_root.mkdir()
    (image_root / "tile_001.jpg").write_bytes(b"fake image")

    annotation_file = tmp_path / "_annotations.coco.json"
    annotation_file.write_text(
        json.dumps(
            {
                "images": [
                    {
                        "id": 1,
                        "file_name": "tile_001.jpg",
                        "width": 512,
                        "height": 512,
                    }
                ],
                "annotations": [
                    {
                        "id": 10,
                        "image_id": 1,
                        "category_id": 3,
                        "bbox": [100, 120, 80, 60],
                        "area": 4800,
                        "iscrowd": 0,
                    }
                ],
                "categories": [{"id": 3, "name": "construction_site"}],
            }
        ),
        encoding="utf-8",
    )

    summary = inspect_coco_dataset(annotation_file, image_root)

    assert summary.image_count == 1
    assert summary.annotation_count == 1
    assert summary.category_count == 1
    assert summary.missing_image_count == 0
    assert summary.empty_image_count == 0
    assert summary.categories == ("construction_site",)


def test_inspector_rejects_annotation_with_missing_image_reference(tmp_path: Path) -> None:
    image_root = tmp_path / "images"
    image_root.mkdir()
    (image_root / "tile_001.jpg").write_bytes(b"fake image")

    annotation_file = tmp_path / "_annotations.coco.json"
    annotation_file.write_text(
        json.dumps(
            {
                "images": [
                    {
                        "id": 1,
                        "file_name": "tile_001.jpg",
                        "width": 512,
                        "height": 512,
                    }
                ],
                "annotations": [
                    {
                        "id": 10,
                        "image_id": 999,
                        "category_id": 3,
                        "bbox": [100, 120, 80, 60],
                    }
                ],
                "categories": [{"id": 3, "name": "construction_site"}],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(CocoInspectionError, match="missing image_id"):
        inspect_coco_dataset(annotation_file, image_root)


def test_inspector_rejects_invalid_bbox(tmp_path: Path) -> None:
    image_root = tmp_path / "images"
    image_root.mkdir()
    (image_root / "tile_001.jpg").write_bytes(b"fake image")

    annotation_file = tmp_path / "_annotations.coco.json"
    annotation_file.write_text(
        json.dumps(
            {
                "images": [
                    {
                        "id": 1,
                        "file_name": "tile_001.jpg",
                        "width": 512,
                        "height": 512,
                    }
                ],
                "annotations": [
                    {
                        "id": 10,
                        "image_id": 1,
                        "category_id": 3,
                        "bbox": [100, 120, 0, 60],
                    }
                ],
                "categories": [{"id": 3, "name": "construction_site"}],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(CocoInspectionError, match="positive"):
        inspect_coco_dataset(annotation_file, image_root)
