from dataclasses import dataclass


@dataclass(frozen=True)
class DetectionCandidate:
    label: str
    confidence: float
    bbox_xyxy: tuple[int, int, int, int]


def run_mock_inference(tile_id: str) -> list[DetectionCandidate]:
    if not tile_id:
        return []
    return [
        DetectionCandidate(
            label="construction_site",
            confidence=0.86,
            bbox_xyxy=(118, 94, 338, 286),
        )
    ]
