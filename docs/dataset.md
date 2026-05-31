# Dataset Pipeline

Milestone 2 starts with the data contract before model training. The first detector target is **RF-DETR Nano**, so the dataset pipeline uses **COCO object detection format**.

## Locked Decisions

- **Model family**: RF-DETR Nano.
- **Task type**: object detection.
- **Annotation format**: COCO JSON.
- **POC dataset**: a small aerial construction dataset exported as COCO JSON.
- **Git policy**: raw datasets stay local and are not committed.
- **Future data versioning**: lakeFS over object storage will version raw data, processed tiles, labels, and manifests.
- **Large-dataset upgrade path**: satellite-native datasets can be added later once the pipeline is validated.

## Expected Layout

```text
data/
  raw/
    <dataset-name>/
      train/
        _annotations.coco.json
        <image files>
      valid/
        _annotations.coco.json
        <image files>
      test/
        _annotations.coco.json
        <image files>
  manifests/
```

Only `.gitkeep` placeholders under `data/` are tracked by Git. Downloaded datasets and generated data artifacts remain local for now. In the MLOps milestone, these artifacts will be moved behind lakeFS commits/tags so data versions are reproducible without storing datasets in Git.

## Inspect A COCO Split

```bash
PYTHONPATH=pipelines uv run python -m dataset.inspect_coco \
  --annotations data/raw/<dataset-name>/train/_annotations.coco.json \
  --images data/raw/<dataset-name>/train \
  --json
```

The inspector validates that:

- required COCO fields exist,
- images and categories are present,
- image files are available on disk,
- annotations reference valid image and category ids,
- bounding boxes are numeric and positive.

## Build A Dataset Manifest

No model training starts until a dataset manifest exists. The manifest captures local source paths, split stats, raw categories, target category policy, and future lakeFS version fields.

```bash
PYTHONPATH=pipelines uv run python -m dataset.build_manifest \
  --dataset-name apoce \
  --dataset-root data/raw/apoce \
  --output data/manifests/apoce_manifest.local.json \
  --provider roboflow \
  --license to_verify
```

Generated manifests are local by default and ignored by Git. Once lakeFS is introduced, equivalent manifests will reference lakeFS commits/tags instead of only local paths.

## Prepare RF-DETR COCO Data

After a manifest exists, prepare a clean training dataset by applying the class policy. The preparation step preserves raw data, drops ignored categories, remaps target classes to stable contiguous IDs, and writes local processed artifacts.

```bash
PYTHONPATH=pipelines uv run python -m dataset.prepare_coco \
  --manifest data/manifests/apoce_manifest.local.json \
  --raw-root data/raw/apoce \
  --output-root data/processed/apoce_rfdetr
```

The output is ignored by Git. It is reproducible from:

- raw dataset files,
- dataset manifest,
- preparation code,
- future lakeFS commit/tag once data versioning is introduced.

## Why This Comes Before Tiling

The model target determines the training format. RF-DETR works naturally with COCO-style object detection data, so the pipeline should preserve COCO annotations and only add tiling once the format contract is stable.

## APOCE POC Notes

The Roboflow COCO export may include a category whose name resembles the dataset/export name. Treat this as source-data metadata to inspect before training. A later preparation step should either drop empty/background categories or map source classes into the project class taxonomy.
