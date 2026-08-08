from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from datetime import datetime, date
from typing import Optional, List
from database import get_db, Patient, MedicalReport, AnalysisHistory
from schemas import DashboardStats, HistoryOut
from auth import get_current_user

dash_router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
hist_router = APIRouter(prefix="/history",   tags=["History"])


@dash_router.get("/stats", response_model=DashboardStats)
def get_stats(
    db: Session = Depends(get_db),
    _: any = Depends(get_current_user),
):
    today_start     = datetime.combine(date.today(), datetime.min.time())
    total_patients  = db.query(func.count(Patient.id)).scalar() or 0
    total_reports   = db.query(func.count(MedicalReport.id)).scalar() or 0
    reports_today   = db.query(func.count(MedicalReport.id)).filter(
        MedicalReport.upload_date >= today_start
    ).scalar() or 0
    recent_patients = db.query(Patient).order_by(Patient.created_at.desc()).limit(5).all()
    recent_reports  = (
        db.query(MedicalReport)
        .options(joinedload(MedicalReport.patient))
        .order_by(MedicalReport.upload_date.desc())
        .limit(5).all()
    )
    return DashboardStats(
        total_patients  = total_patients,
        total_reports   = total_reports,
        reports_today   = reports_today,
        recent_patients = recent_patients,
        recent_reports  = recent_reports,
    )


@hist_router.get("/", response_model=List[HistoryOut])
def list_history(
    patient_id: Optional[str] = Query(None),
    search:     Optional[str] = Query(None),
    skip:  int = Query(0, ge=0),
    limit: int = Query(100, le=200),
    db:    Session = Depends(get_db),
    _:     any = Depends(get_current_user),
):
    q = (
        db.query(AnalysisHistory)
        .options(
            joinedload(AnalysisHistory.patient),
            joinedload(AnalysisHistory.report),
        )
    )
    if patient_id:
        p = db.query(Patient).filter(Patient.patient_id == patient_id.upper()).first()
        if p:
            q = q.filter(AnalysisHistory.patient_id == p.id)
    if search:
        term = f"%{search}%"
        q = q.join(Patient).filter(
            Patient.patient_id.ilike(term) | Patient.name.ilike(term)
        )
    return q.order_by(AnalysisHistory.analysis_date.desc()).offset(skip).limit(limit).all()


@hist_router.delete("/{history_id}", status_code=204)
def delete_history(
    history_id: int,
    db: Session = Depends(get_db),
    _: any = Depends(get_current_user),
):
    record = db.query(AnalysisHistory).filter(AnalysisHistory.id == history_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="History record not found")
    db.delete(record)
    db.commit()