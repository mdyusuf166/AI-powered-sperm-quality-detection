import cv2
import numpy as np
from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.main import create_app


def test_health_endpoint() -> None:
    client = TestClient(create_app())
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_upload_synthetic_image_returns_completed_analysis(tmp_path) -> None:
    app = create_app()
    app.dependency_overrides[get_settings] = lambda: Settings(upload_dir=tmp_path)

    image = np.full((180, 260, 3), 245, dtype=np.uint8)
    cv2.circle(image, (90, 80), 7, (20, 20, 20), -1)
    cv2.circle(image, (150, 120), 6, (30, 30, 30), -1)
    ok, encoded = cv2.imencode(".png", image)
    assert ok

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/analyses/uploads",
            data={
                "patient_code": "TEST-SAMPLE",
                "sample_metadata": '{"microns_per_pixel":0.5,"chamber_depth_microns":20}',
            },
            files={"file": ("synthetic.png", encoded.tobytes(), "image/png")},
        )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "completed"
    assert body["result_json"]["counting"]["detected_cells"] >= 2
    assert "final medical diagnosis" in body["report_json"]["clinical_note"]
