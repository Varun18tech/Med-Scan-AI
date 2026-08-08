import io
import os
import uuid
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db, Patient, MedicalReport, AnalysisHistory
from schemas import ReportOut, ReportWithPatient
from auth import get_current_user

router     = APIRouter(prefix="/reports", tags=["Reports"])
UPLOAD_DIR = "uploads"
ALLOWED    = {"application/pdf", "image/jpeg", "image/png", "image/jpg"}
os.makedirs(UPLOAD_DIR, exist_ok=True)


def extract_pdf(file_bytes: bytes) -> str:
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            return "\n".join(
                page.extract_text() or "" for page in pdf.pages
            ).strip()
    except Exception as e:
        return f"[PDF extraction error: {e}]"


def extract_image(file_bytes: bytes) -> str:
    try:
        import pytesseract
        from PIL import Image
        img  = Image.open(io.BytesIO(file_bytes)).convert("RGB")
        text = pytesseract.image_to_string(img)
        return text.strip() or "[No text found in image]"
    except Exception as e:
        return f"[OCR error: {e}]"


def analyze_text(text: str) -> dict:
    try:
        import torch
        from transformers import pipeline
        device = 0 if torch.cuda.is_available() else -1
        dtype  = torch.float16 if device >= 0 else torch.float32
        summarizer = pipeline(
            "summarization",
            model="facebook/bart-large-cnn",
            device=device,
            torch_dtype=dtype,
        )
        if len(text.split()) > 50:
            simple_raw  = summarizer(text[:1024], max_length=130, min_length=30, do_sample=False)
            medical_raw = summarizer(text[:1024], max_length=200, min_length=50, do_sample=False)
            return {
                "simple_summary":  simple_raw[0]["summary_text"],
                "medical_summary": medical_raw[0]["summary_text"],
            }
    except Exception:
        pass

    words     = text.lower()
    findings  = []
    conditions = {
        "pneumonia":      "A lung infection was detected.",
        "effusion":       "Fluid accumulation was noted.",
        "cardiomegaly":   "The heart appears enlarged.",
        "atelectasis":    "Partial lung collapse was noted.",
        "consolidation":  "Lung consolidation is present.",
        "nodule":         "A lung nodule was detected.",
        "fracture":       "A bone fracture was identified.",
        "normal":         "No significant abnormalities were found.",
        "pneumothorax":   "Air in the chest cavity was detected.",
        "edema":          "Fluid buildup (edema) was noted.",
        "fibrosis":       "Lung scarring (fibrosis) was observed.",
        "mass":           "An abnormal mass was identified.",
        "opacity":        "An opacity was observed in the scan.",
        "infiltrate":     "Infiltrate was noted in the lungs.",
    }
    for key, desc in conditions.items():
        if key in words:
            findings.append(desc)

    if not findings:
        findings = ["Your report has been received. Please consult your doctor for full details."]

    simple  = (
        "Your medical report has been reviewed by our AI system. "
        + " ".join(findings[:3])
        + " These findings are preliminary. Please consult your healthcare provider for a complete explanation and next steps."
    )
    medical = (
        "AI-Assisted Analysis Summary: "
        + "; ".join(findings)
        + f" Document length: {len(text.split())} words. "
        + "Findings are AI-generated and require clinical correlation by a qualified physician."
    )
    return {"simple_summary": simple, "medical_summary": medical}


@router.post("/upload", response_model=ReportOut, status_code=201)
async def upload_report(
    patient_id: str        = Form(...),
    file:       UploadFile = File(...),
    db:         Session    = Depends(get_db),
    _:          any        = Depends(get_current_user),
):
    patient = db.query(Patient).filter(
        Patient.patient_id == patient_id.upper()
    ).first()
    if not patient:
        raise HTTPException(status_code=404, detail=f"Patient '{patient_id}' not found")

    if file.content_type not in ALLOWED:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Use PDF, JPG, or PNG."
        )

    file_bytes = await file.read()
    if len(file_bytes) > 20 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Max 20MB.")

    ext        = file.filename.rsplit(".", 1)[-1].lower()
    saved_name = f"{uuid.uuid4().hex}.{ext}"
    with open(os.path.join(UPLOAD_DIR, saved_name), "wb") as f:
        f.write(file_bytes)

    text     = extract_pdf(file_bytes) if file.content_type == "application/pdf" else extract_image(file_bytes)
    analysis = analyze_text(text or "No text extracted from file")

    report = MedicalReport(
        patient_id      = patient.id,
        file_name       = file.filename,
        file_type       = ext,
        original_text   = (text or "")[:10000],
        simple_summary  = analysis["simple_summary"],
        medical_summary = analysis["medical_summary"],
    )
    db.add(report)
    db.flush()
    db.add(AnalysisHistory(patient_id=patient.id, report_id=report.id))
    db.commit()
    db.refresh(report)
    return report


@router.get("/", response_model=List[ReportWithPatient])
def list_reports(
    patient_id: Optional[str] = None,
    skip:  int = 0,
    limit: int = 50,
    db:    Session = Depends(get_db),
    _:     any = Depends(get_current_user),
):
    from sqlalchemy.orm import joinedload
    q = db.query(MedicalReport).options(joinedload(MedicalReport.patient))
    if patient_id:
        p = db.query(Patient).filter(Patient.patient_id == patient_id.upper()).first()
        if p:
            q = q.filter(MedicalReport.patient_id == p.id)
    return q.order_by(MedicalReport.upload_date.desc()).offset(skip).limit(limit).all()


@router.get("/{report_id}", response_model=ReportWithPatient)
def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    _: any = Depends(get_current_user),
):
    from sqlalchemy.orm import joinedload
    report = (
        db.query(MedicalReport)
        .options(joinedload(MedicalReport.patient))
        .filter(MedicalReport.id == report_id)
        .first()
    )
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.delete("/{report_id}", status_code=204)
def delete_report(
    report_id: int,
    db: Session = Depends(get_db),
    _: any = Depends(get_current_user),
):
    report = db.query(MedicalReport).filter(MedicalReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    db.delete(report)
    db.commit()