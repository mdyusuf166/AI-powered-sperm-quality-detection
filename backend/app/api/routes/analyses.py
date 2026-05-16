from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.security import require_api_key
from app.db.models import Analysis
from app.db.session import get_db
from app.ml.analyzer import SemenAnalyzer, parse_sample_metadata
from app.schemas import AnalysisDetail, AnalysisSummary, ReportResponse
from app.services.storage import media_type_for_filename, save_upload

router = APIRouter(
    prefix="/api/v1/analyses",
    tags=["analyses"],
    dependencies=[Depends(require_api_key)],
)


@router.post("/uploads", response_model=AnalysisDetail, status_code=status.HTTP_201_CREATED)
async def upload_and_analyze(
    file: UploadFile = File(...),
    patient_code: str | None = Form(default=None),
    sample_metadata: str | None = Form(default=None),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> Analysis:
    try:
        metadata = parse_sample_metadata(sample_metadata)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    media_type = media_type_for_filename(file.filename or "")
    saved_path, stored_filename = await save_upload(file, settings)

    analysis = Analysis(
        original_filename=file.filename or stored_filename,
        stored_filename=stored_filename,
        content_type=file.content_type or "application/octet-stream",
        media_type=media_type,
        patient_code=patient_code.strip() if patient_code else None,
        status="processing",
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    analyzer = SemenAnalyzer(settings)
    try:
        result, report = analyzer.analyze_file(saved_path, metadata)
        analysis.result_json = result
        analysis.report_json = report
        analysis.status = "completed"
    except Exception as exc:  # noqa: BLE001 - persist error for dashboard review
        analysis.status = "failed"
        analysis.error_message = str(exc)
    finally:
        db.add(analysis)
        db.commit()
        db.refresh(analysis)

    return analysis


@router.get("", response_model=list[AnalysisSummary])
def list_analyses(
    limit: int = 25,
    db: Session = Depends(get_db),
) -> list[Analysis]:
    limit = min(max(limit, 1), 100)
    statement = select(Analysis).order_by(desc(Analysis.created_at)).limit(limit)
    return list(db.scalars(statement).all())


@router.get("/{analysis_id}", response_model=AnalysisDetail)
def get_analysis(analysis_id: str, db: Session = Depends(get_db)) -> Analysis:
    analysis = db.get(Analysis, analysis_id)
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found.")
    return analysis


@router.get("/{analysis_id}/report", response_model=ReportResponse)
def get_report(analysis_id: str, db: Session = Depends(get_db)) -> ReportResponse:
    analysis = db.get(Analysis, analysis_id)
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found.")
    return ReportResponse(analysis_id=analysis.id, report=analysis.report_json or {})

