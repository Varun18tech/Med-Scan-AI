from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db, Patient
from schemas import PatientCreate, PatientUpdate, PatientOut
from auth import get_current_user

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.post("/", response_model=PatientOut, status_code=201)
def create_patient(
    body: PatientCreate,
    db: Session = Depends(get_db),
    _: any = Depends(get_current_user),
):
    existing = db.query(Patient).filter(
        Patient.patient_id == body.patient_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Patient ID '{body.patient_id}' already exists"
        )
    patient = Patient(**body.dict())
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


@router.get("/", response_model=List[PatientOut])
def list_patients(
    search:       Optional[str] = Query(None),
    patient_type: Optional[str] = Query(None),
    skip:         int = Query(0, ge=0),
    limit:        int = Query(100, le=200),
    db:           Session = Depends(get_db),
    _:            any = Depends(get_current_user),
):
    q = db.query(Patient)
    if search:
        term = f"%{search}%"
        q = q.filter(
            Patient.patient_id.ilike(term) |
            Patient.name.ilike(term) |
            Patient.phone.ilike(term)
        )
    if patient_type:
        q = q.filter(Patient.patient_type == patient_type)
    return q.order_by(Patient.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{patient_id}", response_model=PatientOut)
def get_patient(
    patient_id: str,
    db: Session = Depends(get_db),
    _: any = Depends(get_current_user),
):
    patient = db.query(Patient).filter(
        Patient.patient_id == patient_id.upper()
    ).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.put("/{patient_id}", response_model=PatientOut)
def update_patient(
    patient_id: str,
    body: PatientUpdate,
    db: Session = Depends(get_db),
    _: any = Depends(get_current_user),
):
    patient = db.query(Patient).filter(
        Patient.patient_id == patient_id.upper()
    ).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    for field, value in body.dict(exclude_unset=True).items():
        setattr(patient, field, value)
    db.commit()
    db.refresh(patient)
    return patient


@router.delete("/{patient_id}", status_code=204)
def delete_patient(
    patient_id: str,
    db: Session = Depends(get_db),
    _: any = Depends(get_current_user),
):
    patient = db.query(Patient).filter(
        Patient.patient_id == patient_id.upper()
    ).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    db.delete(patient)
    db.commit()