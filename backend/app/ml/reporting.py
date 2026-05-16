from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


DISCLAIMER = (
    "Research and clinical decision-support only. This system does not provide a final medical diagnosis. "
    "Results require validation by qualified clinicians or accredited andrology laboratory personnel."
)


def generate_fertility_report(analysis_result: dict[str, Any]) -> dict[str, Any]:
    count = analysis_result.get("counting", {})
    motility = analysis_result.get("motility", {})
    morphology = analysis_result.get("morphology", {})
    warnings = list(analysis_result.get("warnings", []))

    concentration = count.get("concentration_million_per_ml")
    progressive = motility.get("progressive_percent")
    normal_like = morphology.get("normal_like_percent")

    interpretation: list[str] = []
    flags: list[str] = []

    if concentration is None:
        flags.append("calibration_required_for_concentration")
        interpretation.append("Concentration could not be estimated because calibration or chamber geometry is missing.")
    elif concentration < 16:
        flags.append("low_concentration_screen")
        interpretation.append("Estimated concentration is below a common WHO-style lower reference screening threshold.")
    else:
        interpretation.append("Estimated concentration is not flagged by the configured screening threshold.")

    if progressive is None:
        flags.append("video_required_for_motility")
        interpretation.append("Motility analysis requires video or a sequence with reliable frame timing.")
    elif progressive < 30:
        flags.append("low_progressive_motility_screen")
        interpretation.append("Progressive motility is below the configured screening threshold.")
    else:
        interpretation.append("Progressive motility is not flagged by the configured screening threshold.")

    if normal_like is None:
        flags.append("morphology_unavailable")
    elif normal_like < 4:
        flags.append("low_normal_like_morphology_screen")
        interpretation.append("Normal-like morphology is below the configured strict-screening threshold.")

    if not interpretation:
        interpretation.append("No major automated screening flags were produced.")

    return {
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "summary": {
            "decision_support_flags": flags,
            "interpretation": interpretation,
            "risk_level": _risk_level(flags),
        },
        "key_metrics": {
            "estimated_concentration_million_per_ml": concentration,
            "progressive_motility_percent": progressive,
            "normal_like_morphology_percent": normal_like,
            "tracked_cells": motility.get("tracked_cells"),
            "detected_cells": count.get("detected_cells"),
        },
        "warnings": warnings,
        "clinical_note": DISCLAIMER,
        "privacy_note": (
            "Store only coded patient identifiers, encrypt media at rest in production, "
            "restrict access by role, and follow applicable medical data regulations."
        ),
    }


def _risk_level(flags: list[str]) -> str:
    severe_flags = {
        "low_concentration_screen",
        "low_progressive_motility_screen",
        "low_normal_like_morphology_screen",
    }
    if len(severe_flags.intersection(flags)) >= 2:
        return "high_screening_attention"
    if severe_flags.intersection(flags):
        return "moderate_screening_attention"
    if flags:
        return "review_required"
    return "no_automated_flags"
