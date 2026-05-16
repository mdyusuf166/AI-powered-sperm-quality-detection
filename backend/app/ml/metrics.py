from __future__ import annotations

from dataclasses import dataclass
from math import atan2, hypot, pi
from statistics import median

import numpy as np

from app.ml.detection import Detection
from app.ml.tracking import Track


@dataclass(slots=True)
class SampleCalibration:
    microns_per_pixel: float
    chamber_depth_microns: float


@dataclass(slots=True)
class TrackMetrics:
    track_id: int
    duration_seconds: float
    path_length_microns: float
    displacement_microns: float
    curvilinear_velocity_um_s: float
    straight_line_velocity_um_s: float
    linearity: float
    turn_angle_std_degrees: float
    motility_class: str
    abnormal_pattern: str | None


def estimate_concentration_million_per_ml(
    count: int,
    frame_shape: tuple[int, int, int] | tuple[int, int],
    calibration: SampleCalibration | None,
) -> float | None:
    """Estimate concentration from visible field volume.

    This needs microscope calibration and counting chamber geometry. Without
    those values, returning a number would look precise but be scientifically
    weak, so the function returns None.
    """

    if calibration is None:
        return None

    height_px, width_px = frame_shape[:2]
    width_mm = (width_px * calibration.microns_per_pixel) / 1000.0
    height_mm = (height_px * calibration.microns_per_pixel) / 1000.0
    depth_mm = calibration.chamber_depth_microns / 1000.0
    volume_ul = width_mm * height_mm * depth_mm
    volume_ml = volume_ul / 1000.0
    if volume_ml <= 0:
        return None
    return float((count / volume_ml) / 1_000_000.0)


def summarize_morphology(detections: list[Detection]) -> dict:
    if not detections:
        return {
            "assessed_cells": 0,
            "normal_like_percent": None,
            "abnormal_like_percent": None,
            "median_area_px": None,
            "median_aspect_ratio": None,
            "notes": ["No cells available for morphology screening."],
        }

    areas = [d.area_px for d in detections]
    aspect_ratios = [d.aspect_ratio for d in detections]
    circularities = [d.circularity for d in detections]
    median_area = float(median(areas))
    median_aspect = float(median(aspect_ratios))

    abnormal = 0
    for detection in detections:
        area_low = detection.area_px < median_area * 0.45
        area_high = detection.area_px > median_area * 2.25
        elongated = detection.aspect_ratio > max(3.5, median_aspect * 2.2)
        irregular = detection.circularity and detection.circularity < 0.18
        if area_low or area_high or elongated or irregular:
            abnormal += 1

    assessed = len(detections)
    abnormal_percent = (abnormal / assessed) * 100.0
    return {
        "assessed_cells": assessed,
        "normal_like_percent": round(100.0 - abnormal_percent, 2),
        "abnormal_like_percent": round(abnormal_percent, 2),
        "median_area_px": round(median_area, 2),
        "median_aspect_ratio": round(median_aspect, 2),
        "notes": [
            "Morphology screening is image-derived and must be confirmed by trained embryology or laboratory review."
        ],
    }


def compute_track_metrics(
    tracks: list[Track],
    calibration: SampleCalibration | None,
    progressive_threshold_um_s: float = 25.0,
    motile_threshold_um_s: float = 5.0,
) -> list[TrackMetrics]:
    microns_per_pixel = calibration.microns_per_pixel if calibration else 1.0
    metrics: list[TrackMetrics] = []

    for track in tracks:
        if len(track.points) < 2:
            continue

        points = track.points
        duration = points[-1].time_seconds - points[0].time_seconds
        if duration <= 0:
            continue

        segment_lengths_px: list[float] = []
        angles: list[float] = []
        for previous, current in zip(points, points[1:], strict=False):
            dx = current.x - previous.x
            dy = current.y - previous.y
            segment_lengths_px.append(hypot(dx, dy))
            angles.append(atan2(dy, dx))

        path_length = sum(segment_lengths_px) * microns_per_pixel
        displacement = hypot(points[-1].x - points[0].x, points[-1].y - points[0].y) * microns_per_pixel
        vcl = path_length / duration
        vsl = displacement / duration
        linearity = displacement / path_length if path_length > 0 else 0.0

        turn_std = 0.0
        if len(angles) >= 2:
            deltas = []
            for previous, current in zip(angles, angles[1:], strict=False):
                delta = (current - previous + pi) % (2 * pi) - pi
                deltas.append(abs(delta) * 180.0 / pi)
            turn_std = float(np.std(deltas)) if deltas else 0.0

        if vsl >= progressive_threshold_um_s and linearity >= 0.45:
            motility_class = "progressive"
        elif vcl >= motile_threshold_um_s:
            motility_class = "non_progressive"
        else:
            motility_class = "immotile_or_minimally_motile"

        abnormal_pattern = None
        if vcl >= progressive_threshold_um_s and linearity < 0.2:
            abnormal_pattern = "fast_circular_or_erratic_motion"
        elif turn_std > 85.0 and vcl > motile_threshold_um_s:
            abnormal_pattern = "high_turning_variability"
        elif vcl < motile_threshold_um_s and displacement < 3.0:
            abnormal_pattern = "low_movement_or_adherent_cell"

        metrics.append(
            TrackMetrics(
                track_id=track.id,
                duration_seconds=round(duration, 3),
                path_length_microns=round(path_length, 3),
                displacement_microns=round(displacement, 3),
                curvilinear_velocity_um_s=round(vcl, 3),
                straight_line_velocity_um_s=round(vsl, 3),
                linearity=round(linearity, 3),
                turn_angle_std_degrees=round(turn_std, 3),
                motility_class=motility_class,
                abnormal_pattern=abnormal_pattern,
            )
        )

    return metrics


def summarize_motility(track_metrics: list[TrackMetrics]) -> dict:
    total = len(track_metrics)
    if total == 0:
        return {
            "tracked_cells": 0,
            "progressive_percent": None,
            "non_progressive_percent": None,
            "immotile_percent": None,
            "mean_vcl_um_s": None,
            "mean_vsl_um_s": None,
            "abnormal_patterns": {},
        }

    progressive = sum(1 for metric in track_metrics if metric.motility_class == "progressive")
    non_progressive = sum(1 for metric in track_metrics if metric.motility_class == "non_progressive")
    immotile = total - progressive - non_progressive
    abnormal_patterns: dict[str, int] = {}
    for metric in track_metrics:
        if metric.abnormal_pattern:
            abnormal_patterns[metric.abnormal_pattern] = abnormal_patterns.get(metric.abnormal_pattern, 0) + 1

    return {
        "tracked_cells": total,
        "progressive_percent": round((progressive / total) * 100.0, 2),
        "non_progressive_percent": round((non_progressive / total) * 100.0, 2),
        "immotile_percent": round((immotile / total) * 100.0, 2),
        "mean_vcl_um_s": round(float(np.mean([m.curvilinear_velocity_um_s for m in track_metrics])), 3),
        "mean_vsl_um_s": round(float(np.mean([m.straight_line_velocity_um_s for m in track_metrics])), 3),
        "abnormal_patterns": abnormal_patterns,
    }

