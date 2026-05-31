import json
from pathlib import Path

from dataset.build_manifest import DatasetManifestConfig, write_dataset_manifest


def test_build_manifest_records_splits_and_versioning(tmp_path: Path) -> None:
    dataset_root = tmp_path / "raw" / "demo"
    for split in ("train", "valid", "test"):
        split_root = dataset_root / split
        split_root.mkdir(parents=True)
        (split_root / f"{split}_001.jpg").write_bytes(b"fake image")
        (split_root / "_annotations.coco.json").write_text(
            json.dumps(
                {
                    "images": [
                        {
                            "id": 1,
                            "file_name": f"{split}_001.jpg",
                            "width": 512,
                            "height": 512,
                        }
                    ],
                    "annotations": [
                        {
                            "id": 1,
                            "image_id": 1,
                            "category_id": 2,
                            "bbox": [10, 20, 30, 40],
                        }
                    ],
                    "categories": [
                        {"id": 1, "name": "demo-object-detection-export-name"},
                        {"id": 2, "name": "excavator"},
                    ],
                }
            ),
            encoding="utf-8",
        )

    output_file = tmp_path / "manifests" / "demo_manifest.json"

    manifest = write_dataset_manifest(
        DatasetManifestConfig(
            dataset_name="demo",
            dataset_root=dataset_root,
            output_file=output_file,
        )
    )

    assert output_file.is_file()
    assert manifest["dataset_name"] == "demo"
    assert manifest["target_model_family"] == "rf-detr"
    assert manifest["versioning"]["current_mode"] == "local_only"
    assert manifest["versioning"]["future_system"] == "lakefs"
    assert manifest["splits"]["train"]["image_count"] == 1
    assert manifest["class_policy"]["ignored_categories"] == ["demo-object-detection-export-name"]
    assert manifest["class_policy"]["target_categories"] == ["excavator"]
