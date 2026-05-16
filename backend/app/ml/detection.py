from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import cv2
import numpy as np


@dataclass(slots=True)
class Detection:
    bbox_xyxy: tuple[float, float, float, float]
    centroid_xy: tuple[float, float]
    confidence: float
    area_px: float
    perimeter_px: float
    circularity: float
    aspect_ratio: float
    class_name: str = "sperm"


class SpermDetector(Protocol):
    def detect(self, frame_bgr: np.ndarray) -> list[Detection]:
        ...


class ClassicalSpermDetector:
    """Deterministic OpenCV baseline for research prototypes.

    This detects high-contrast sperm heads and cell-like objects. It is not a
    substitute for a validated YOLO/segmentation model trained on microscopy
    data, but it gives the platform a testable baseline.
    """

    def __init__(
        self,
        min_area_px: int = 12,
        max_area_px: int = 1400,
        min_circularity: float = 0.08,
    ) -> None:
        self.min_area_px = min_area_px
        self.max_area_px = max_area_px
        self.min_circularity = min_circularity

    def detect(self, frame_bgr: np.ndarray) -> list[Detection]:
        if frame_bgr.size == 0:
            return []

        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        blurred = cv2.GaussianBlur(enhanced, (5, 5), 0)

        _, otsu = cv2.threshold(
            blurred,
            0,
            255,
            cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU,
        )
        adaptive = cv2.adaptiveThreshold(
            blurred,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            31,
            3,
        )
        mask = cv2.bitwise_or(otsu, adaptive)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        detections: list[Detection] = []

        for contour in contours:
            area = float(cv2.contourArea(contour))
            if area < self.min_area_px or area > self.max_area_px:
                continue

            perimeter = float(cv2.arcLength(contour, closed=True))
            if perimeter <= 0:
                continue

            circularity = float((4.0 * np.pi * area) / (perimeter * perimeter))
            if circularity < self.min_circularity:
                continue

            x, y, w, h = cv2.boundingRect(contour)
            if w <= 1 or h <= 1:
                continue

            moments = cv2.moments(contour)
            if moments["m00"] == 0:
                cx, cy = x + w / 2.0, y + h / 2.0
            else:
                cx = moments["m10"] / moments["m00"]
                cy = moments["m01"] / moments["m00"]

            aspect_ratio = float(max(w, h) / max(1, min(w, h)))
            confidence = min(0.95, 0.35 + circularity * 0.35 + min(area / self.max_area_px, 1.0) * 0.25)

            detections.append(
                Detection(
                    bbox_xyxy=(float(x), float(y), float(x + w), float(y + h)),
                    centroid_xy=(float(cx), float(cy)),
                    confidence=float(confidence),
                    area_px=area,
                    perimeter_px=perimeter,
                    circularity=circularity,
                    aspect_ratio=aspect_ratio,
                )
            )

        return detections


class YOLOSpermDetector:
    """YOLO adapter for trained sperm detection or segmentation weights."""

    def __init__(self, weights_path: str, confidence_threshold: float = 0.25) -> None:
        if not Path(weights_path).exists():
            raise FileNotFoundError(f"YOLO weights not found: {weights_path}")
        try:
            from ultralytics import YOLO
        except ImportError as exc:
            raise RuntimeError("Install ultralytics to use YOLO detection.") from exc

        self.model = YOLO(weights_path)
        self.confidence_threshold = confidence_threshold

    def detect(self, frame_bgr: np.ndarray) -> list[Detection]:
        results = self.model.predict(frame_bgr, conf=self.confidence_threshold, verbose=False)
        detections: list[Detection] = []
        if not results:
            return detections

        result = results[0]
        boxes = getattr(result, "boxes", None)
        if boxes is None:
            return detections

        xyxy = boxes.xyxy.cpu().numpy()
        confs = boxes.conf.cpu().numpy()
        names = result.names or {}
        cls_values = boxes.cls.cpu().numpy() if boxes.cls is not None else np.zeros(len(xyxy))

        for box, conf, cls_idx in zip(xyxy, confs, cls_values, strict=False):
            x1, y1, x2, y2 = [float(v) for v in box]
            w = max(1.0, x2 - x1)
            h = max(1.0, y2 - y1)
            area = w * h
            perimeter = 2.0 * (w + h)
            aspect_ratio = max(w, h) / max(1.0, min(w, h))
            detections.append(
                Detection(
                    bbox_xyxy=(x1, y1, x2, y2),
                    centroid_xy=((x1 + x2) / 2.0, (y1 + y2) / 2.0),
                    confidence=float(conf),
                    area_px=float(area),
                    perimeter_px=float(perimeter),
                    circularity=0.0,
                    aspect_ratio=float(aspect_ratio),
                    class_name=str(names.get(int(cls_idx), "sperm")),
                )
            )

        return detections


def build_detector(weights_path: str | None) -> SpermDetector:
    if weights_path:
        return YOLOSpermDetector(weights_path)
    return ClassicalSpermDetector()

