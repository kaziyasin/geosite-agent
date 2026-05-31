import json
from pathlib import Path

from dataset.prepare_coco import CocoPreparationConfig, prepare_coco_dataset


def test_prepare_coco_drops_ignored_category_and_remaps_targets(tmp_path: Path) -> None:
    raw_root = tmp_path / "raw" / "demo"
    for split in ("train", "valid", "test"):
        split_root = raw_root / split
        split_root.mkdir(parents=True)
        (split_root / f"{split}_001.jpg").write_bytes(b"fake image")
        (split_root / f"{split}_002.jpg").write_bytes(b"fake image")
        (split_root / "_annotations.coco.json").write_text(
            json.dumps(
                {
                    "images": [
                        {
                            "id": 10,
                            "file_name": f"{split}_001.jpg",
                            "width": 512,
                            "height": 512,
                        },
                        {
                            "id": 20,
                            "file_name": f"{split}_002.jpg",
                            "width": 512,
                            "height": 512,
                        },
                    ],
                    "annotations": [
                        {
                            "id": 100,
                            "image_id": 10,
                            "category_id": 9,
                            "bbox": [1, 2, 3, 4],
                        },
                        {
                            "id": 101,
                            "image_id": 20,
                            "category_id": 1,
                            "bbox": [5, 6, 7, 8],
                        },
                    ],
                    "categories": [
                        {"id": 1, "name": "demo-object-detection-export-name"},
                        {"id": 9, "name": "excavator"},
                    ],
                }
            ),
            encoding="utf-8",
        )

    manifest_file = tmp_path / "manifest.json"
    manifest_file.write_text(
        json.dumps(
            {
                "class_policy": {
                    "ignored_categories": ["demo-object-detection-export-name"],
                    "target_categories": ["excavator"],
                },
                "versioning": {
                    "lakefs_repo": "geosite-agent",
                },
            }
        ),
        encoding="utf-8",
    )
    output_root = tmp_path / "processed" / "demo_rfdetr"

    metadata = prepare_coco_dataset(
        CocoPreparationConfig(
            manifest_file=manifest_file,
            raw_dataset_root=raw_root,
            output_root=output_root,
        )
    )

    assert metadata["versioning"]["future_system"] == "lakefs"
    assert metadata["splits"]["train"]["image_count"] == 1
    assert metadata["splits"]["train"]["annotation_count"] == 1
    assert metadata["splits"]["train"]["dropped_annotation_count"] == 1
    assert (output_root / "train" / "train_001.jpg").is_file()
    assert not (output_root / "train" / "train_002.jpg").exists()

    cleaned = json.loads((output_root / "train" / "_annotations.coco.json").read_text())
    assert cleaned["categories"] == [{"id": 1, "name": "excavator"}]
    assert cleaned["annotations"][0]["id"] == 1
    assert cleaned["annotations"][0]["category_id"] == 1
    assert cleaned["images"][0]["file_name"] == "train_001.jpg"
