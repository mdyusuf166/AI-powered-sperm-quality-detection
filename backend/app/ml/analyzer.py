from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

import cv2
import numpy as np

from app.core.config import Settings
from app.ml.detection import Detection, SpermDetector, build_detector
from app.ml.metrics import (
    SampleCalibration,
    compute_track_metrics,
    estimate_concentration_million_per_ml,
    summarize_morphology,
    summarize_motility,
)
from app.ml.reporting import generate_fertility_report
from app.ml.tracking import SpermTracker
from app.services.serialization import to_builtin
from app.services.storage import media_type_for_filename


class SemenAnalyzer:
    def __init__(self, settings: Settings, detector: SpermDetector | None = None) -> None:
        self.settings = settings
        self.detector = detector or build_detector(settings.yolo_weights_path)

    def analyze_file(
        self,
        file_path: Path,
        sample_metadata: dict[str, Any] | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        sample_metadata = sample_metadata or {}
        media_type = media_type_for_filename(file_path.name)
        if media_type == "image":
            result = self._analyze_image(file_path, sample_metadata)
        else:
            result = self._analyze_video(file_path, sample_metadata)

        report = generate_fertility_report(result)
        return to_builtin(result), to_builtin(report)

    def _calibration(self, sample_metadata: dict[str, Any]) -> SampleCalibration | None:
        microns_per_pixel = sample_metadata.get("microns_per_pixel", self.settings.default_microns_per_pixel)
        chamber_depth = sample_metadata.get(
            "chamber_depth_microns",
            self.settings.default_chamber_depth_microns,
        )
        if microns_per_pixel is None or chamber_depth is None:
            return None
        try:
            return SampleCalibration(
                microns_per_pixel=float(microns_per_pixel),
                chamber_depth_microns=float(chamber_depth),
            )
        except (TypeError, ValueError):
            return None

    def _analyze_image(self, file_path: Path, sample_metadata: dict[str, Any]) -> dict[str, Any]:
        frame = cv2.imread(str(file_path))
        if frame is None:
            raise ValueError("Could not decode uploaded image.")

        calibration = self._calibration(sample_metadata)
        detections = self.detector.detect(frame)
        concentration = estimate_concentration_million_per_ml(len(detections), frame.shape, calibration)
        morphology = summarize_morphology(detections)

        warnings = [
            "Single-image analysis cannot estimate motility; upload video for speed and path metrics.",
            "Concentration estimates depend on microscope calibration and counting chamber geometry.",
        ]
        if calibration is None:
            warnings.append("No valid calibration available; concentration omitted.")

        return {
            "media_type": "image",
            "frame_count_analyzed": 1,
            "frame_shape": list(frame.shape),
            "counting": {
                "detected_cells": len(detections),
                "concentration_million_per_ml": _round_optional(concentration),
            },
            "detections": [_detection_to_dict(detection) for detection in detections],
            "motility": {
                "tracked_cells": 0,
                "progressive_percent": None,
                "non_progressive_percent": None,
                "immotile_percent": None,
                "mean_vcl_um_s": None,
                "mean_vsl_um_s": None,
                "abnormal_patterns": {},
            },
            "tracks": [],
            "morphology": morphology,
            "metadata": _metadata_for_result(sample_metadata, calibration),
            "warnings": warnings,
        }

    def _analyze_video(self, file_path: Path, sample_metadata: dict[str, Any]) -> dict[str, Any]:
        capture = cv2.VideoCapture(str(file_path))
        if not capture.isOpened():
            raise ValueError("Could not decode uploaded video.")

        fps = float(capture.get(cv2.CAP_PROP_FPS) or sample_metadata.get("fps") or 30.0)
        total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        max_frames = int(sample_metadata.get("max_frames", 300))
        frame_stride = max(1, int(sample_metadata.get("frame_stride", 1)))

        calibration = self._calibration(sample_metadata)
        tracker = SpermTracker(max_link_distance_px=float(sample_metadata.get("max_link_distance_px", 32.0)))
        all_detections: list[Detection] = []
        first_shape: tuple[int, int, int] | None = None
        analyzed_frames = 0
        frame_index = 0

        while analyzed_frames < max_frames:
            ok, frame = capture.read()
            if not ok:
                break

            if frame_index % frame_stride != 0:
                frame_index += 1
                continue

            if first_shape is None:
                first_shape = frame.shape

            detections = self.detector.detect(frame)
            all_detections.extend(detections)
            tracker.update(detections, frame_index=frame_index, time_seconds=frame_index / fps)
            analyzed_frames += 1
            frame_index += 1

        capture.release()

        tracks = tracker.tracks(min_points=int(sample_metadata.get("min_track_points", 3)))
        track_metrics = compute_track_metrics(tracks, calibration)
        motility = summarize_motility(track_metrics)

        mean_count = int(round(len(all_detections) / analyzed_frames)) if analyzed_frames else 0
        concentration = None
        if first_shape is not None:
            concentration = estimate_concentration_million_per_ml(mean_count, first_shape, calibration)

        warnings = [
            "Video analysis uses nearest-neighbor tracking and should be validated against manual CASA-style review.",
            "Concentration is estimated from mean detected cells per analyzed field; use calibrated chamber protocols for clinical use.",
        ]
        if calibration is None:
            warnings.append("No valid calibration available; speed remains in pixels/second equivalent and concentration is omitted.")
        if total_frames and analyzed_frames < total_frames:
            warnings.append(f"Analyzed {analyzed_frames} sampled frames from {total_frames} total frames.")

        return {
            "media_type": "video",
            "frame_count_total": total_frames,
            "frame_count_analyzed": analyzed_frames,
            "fps": fps,
            "frame_shape": list(first_shape) if first_shape else None,
            "counting": {
                "detected_cells": mean_count,
                "total_detections_across_frames": len(all_detections),
                "concentration_million_per_ml": _round_optional(concentration),
            },
            "motility": motility,
            "tracks": [asdict(track_metric) for track_metric in track_metrics[:500]],
            "morphology": summarize_morphology(all_detections[:1000]),
            "metadata": _metadata_for_result(sample_metadata, calibration),
            "warnings": warnings,
        }


def parse_sample_metadata(raw_metadata: str | None) -> dict[str, Any]:
    if not raw_metadata:
        return {}
    try:
        parsed = json.loads(raw_metadata)
    except json.JSONDecodeError as exc:
        raise ValueError("sample_metadata must be valid JSON.") from exc
    if not isinstance(parsed, dict):
        raise ValueError("sample_metadata must be a JSON object.")
    return parsed


def _detection_to_dict(detection: Detection) -> dict[str, Any]:
    return {
        "bbox_xyxy": [round(value, 3) for value in detection.bbox_xyxy],
        "centroid_xy": [round(value, 3) for value in detection.centroid_xy],
        "confidence": round(detection.confidence, 4),
        "area_px": round(detection.area_px, 3),
        "perimeter_px": round(detection.perimeter_px, 3),
        "circularity": round(detection.circularity, 4),
        "aspect_ratio": round(detection.aspect_ratio, 4),
        "class_name": detection.class_name,
    }


def _metadata_for_result(sample_metadata: dict[str, Any], calibration: SampleCalibration | None) -> dict[str, Any]:
    return {
        "provided": sample_metadata,
        "calibration": asdict(calibration) if calibration else None,
        "model": "YOLO/segmentation" if sample_metadata.get("model_name") else "classical_opencv_baseline",
    }


def _round_optional(value: float | None) -> float | None:
    if value is None or not np.isfinite(value):
        return None
    return round(float(value), 3)
