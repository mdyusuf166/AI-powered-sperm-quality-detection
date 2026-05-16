from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AnalysisSummary(BaseModel):
    id: str
    original_filename: str
    media_type: str
    patient_code: str | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AnalysisDetail(AnalysisSummary):
    result_json: dict[str, Any] | None
    report_json: dict[str, Any] | None
    error_message: str | None

    model_config = {"from_attributes": True}


class ReportResponse(BaseModel):
    analysis_id: str
    report: dict[str, Any] = Field(default_factory=dict)

