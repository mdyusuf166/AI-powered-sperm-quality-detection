import cv2
import numpy as np

from app.core.config import Settings
from app.ml.analyzer import SemenAnalyzer


def test_synthetic_image_analysis_detects_cells(tmp_path) -> None:
    image = np.full((240, 320, 3), 245, dtype=np.uint8)
    cv2.circle(image, (80, 90), 7, (30, 30, 30), -1)
    cv2.circle(image, (150, 130), 6, (20, 20, 20), -1)
    cv2.circle(image, (220, 170), 8, (35, 35, 35), -1)

    image_path = tmp_path / "synthetic_sample.png"
    assert cv2.imwrite(str(image_path), image)

    analyzer = SemenAnalyzer(Settings(upload_dir=tmp_path))
    result, report = analyzer.analyze_file(
        image_path,
        {"microns_per_pixel": 0.5, "chamber_depth_microns": 20},
    )

    assert result["counting"]["detected_cells"] >= 3
    assert result["media_type"] == "image"
    assert "clinical decision-support" in report["clinical_note"]

