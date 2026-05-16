from app.ml.metrics import SampleCalibration, estimate_concentration_million_per_ml, summarize_motility
from app.ml.tracking import Track, TrackPoint
from app.ml.metrics import compute_track_metrics


def test_concentration_requires_calibration() -> None:
    assert estimate_concentration_million_per_ml(10, (100, 100, 3), None) is None


def test_concentration_estimate_with_calibration() -> None:
    calibration = SampleCalibration(microns_per_pixel=1.0, chamber_depth_microns=20.0)
    value = estimate_concentration_million_per_ml(20, (1000, 1000, 3), calibration)
    assert value is not None
    assert round(value, 3) == 1.0


def test_progressive_track_summary() -> None:
    track = Track(id=1)
    track.points = [
        TrackPoint(frame_index=0, time_seconds=0.0, x=0.0, y=0.0),
        TrackPoint(frame_index=1, time_seconds=1.0, x=40.0, y=0.0),
    ]
    metrics = compute_track_metrics([track], SampleCalibration(microns_per_pixel=1.0, chamber_depth_microns=20.0))
    summary = summarize_motility(metrics)
    assert summary["tracked_cells"] == 1
    assert summary["progressive_percent"] == 100.0

