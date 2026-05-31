import json
from pathlib import Path

from training.reproducibility import collect_reproducibility_metadata, write_reproducibility_metadata


def test_reproducibility_metadata_tracks_core_training_inputs(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (repo_root / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")
    (repo_root / "uv.lock").write_text("# lock\n", encoding="utf-8")
    (repo_root / ".python-version").write_text("3.13\n", encoding="utf-8")

    dataset_manifest = tmp_path / "manifest.json"
    dataset_manifest.write_text(
        json.dumps(
            {
                "versioning": {
                    "lakefs_repo": "geosite-agent",
                    "lakefs_branch": "main",
                    "lakefs_commit": "abc123",
                    "lakefs_tag": "dataset-v0.1",
                }
            }
        ),
        encoding="utf-8",
    )
    prepared_metadata = tmp_path / "prepared.json"
    prepared_metadata.write_text('{"splits": {}}\n', encoding="utf-8")

    metadata = collect_reproducibility_metadata(
        repo_root=repo_root,
        dataset_manifest_path=dataset_manifest,
        prepared_metadata_path=prepared_metadata,
    )

    assert metadata["reproducibility_contract_version"] == "1.0"
    assert metadata["mlops"]["orchestrator"] == "zenml"
    assert metadata["mlops"]["experiment_tracker"] == "mlflow"
    assert metadata["dependencies"]["pyproject"]["exists"] is True
    assert metadata["dependencies"]["uv_lock"]["exists"] is True
    assert metadata["dependencies"]["python_version_file"]["exists"] is True
    assert metadata["data_lineage"]["dataset_manifest"]["exists"] is True
    assert metadata["data_lineage"]["prepared_metadata"]["exists"] is True
    assert metadata["data_lineage"]["lakefs"]["commit"] == "abc123"
    assert "hardware" in metadata
    assert "cpu_count" in metadata["hardware"]


def test_write_reproducibility_metadata(tmp_path: Path) -> None:
    output = tmp_path / "repro.json"

    write_reproducibility_metadata(output, {"ok": True})

    assert json.loads(output.read_text(encoding="utf-8")) == {"ok": True}
