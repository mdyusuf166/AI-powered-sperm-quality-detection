from __future__ import annotations

from dataclasses import dataclass, field
from math import hypot

from app.ml.detection import Detection


@dataclass(slots=True)
class TrackPoint:
    frame_index: int
    time_seconds: float
    x: float
    y: float


@dataclass(slots=True)
class Track:
    id: int
    points: list[TrackPoint] = field(default_factory=list)
    missed_frames: int = 0

    @property
    def last_point(self) -> TrackPoint | None:
        return self.points[-1] if self.points else None

    def add(self, point: TrackPoint) -> None:
        self.points.append(point)
        self.missed_frames = 0


class SpermTracker:
    """Nearest-neighbor multi-object tracker for microscopy footage."""

    def __init__(self, max_link_distance_px: float = 32.0, max_missed_frames: int = 4) -> None:
        self.max_link_distance_px = max_link_distance_px
        self.max_missed_frames = max_missed_frames
        self._next_id = 1
        self._active: list[Track] = []
        self._finished: list[Track] = []

    def update(self, detections: list[Detection], frame_index: int, time_seconds: float) -> None:
        unmatched_detection_indexes = set(range(len(detections)))
        unmatched_track_indexes = set(range(len(self._active)))
        candidate_links: list[tuple[float, int, int]] = []

        for track_index, track in enumerate(self._active):
            last = track.last_point
            if last is None:
                continue
            for detection_index, detection in enumerate(detections):
                cx, cy = detection.centroid_xy
                distance = hypot(cx - last.x, cy - last.y)
                if distance <= self.max_link_distance_px:
                    candidate_links.append((distance, track_index, detection_index))

        for _, track_index, detection_index in sorted(candidate_links, key=lambda item: item[0]):
            if track_index not in unmatched_track_indexes or detection_index not in unmatched_detection_indexes:
                continue
            detection = detections[detection_index]
            cx, cy = detection.centroid_xy
            self._active[track_index].add(
                TrackPoint(
                    frame_index=frame_index,
                    time_seconds=time_seconds,
                    x=float(cx),
                    y=float(cy),
                )
            )
            unmatched_track_indexes.remove(track_index)
            unmatched_detection_indexes.remove(detection_index)

        for track_index in list(unmatched_track_indexes):
            track = self._active[track_index]
            track.missed_frames += 1

        still_active: list[Track] = []
        for track in self._active:
            if track.missed_frames > self.max_missed_frames:
                self._finished.append(track)
            else:
                still_active.append(track)
        self._active = still_active

        for detection_index in unmatched_detection_indexes:
            detection = detections[detection_index]
            cx, cy = detection.centroid_xy
            track = Track(id=self._next_id)
            self._next_id += 1
            track.add(
                TrackPoint(
                    frame_index=frame_index,
                    time_seconds=time_seconds,
                    x=float(cx),
                    y=float(cy),
                )
            )
            self._active.append(track)

    def tracks(self, min_points: int = 2) -> list[Track]:
        return [track for track in [*self._finished, *self._active] if len(track.points) >= min_points]

