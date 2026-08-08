from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime


class UserCreate(BaseModel):
    name:     str
    email:    EmailStr
    password: str
    role:     Optional[str] = "staff"

    @validator("password")
    def password_strength(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v

    @validator("name")
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()


class UserLogin(BaseModel):
    email:    EmailStr
    password: str


class UserOut(BaseModel):
    id:         int
    name:       str
    email:      str
    role:       str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type:   str
    user:         UserOut


class PatientCreate(BaseModel):
    patient_id:   str
    name:         str
    age:          int
    gender:       str
    phone:        Optional[str] = ""
    patient_type: Optional[str] = "General"

    @validator("age")
    def valid_age(cls, v):
        if not (0 < v < 150):
            raise ValueError("Age must be between 1 and 149")
        return v

    @validator("patient_id")
    def valid_pid(cls, v):
        if not v.strip():
            raise ValueError("Patient ID cannot be empty")
        return v.strip().upper()

    @validator("name")
    def valid_name(cls, v):
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()


class PatientUpdate(BaseModel):
    name:         Optional[str]
    age:          Optional[int]
    gender:       Optional[str]
    phone:        Optional[str]
    patient_type: Optional[str]


class PatientOut(BaseModel):
    id:           int
    patient_id:   str
    name:         str
    age:          int
    gender:       str
    phone:        Optional[str]
    patient_type: str
    created_at:   datetime

    class Config:
        from_attributes = True


class ReportOut(BaseModel):
    id:              int
    patient_id:      int
    file_name:       str
    file_type:       Optional[str]
    original_text:   Optional[str]
    simple_summary:  Optional[str]
    medical_summary: Optional[str]
    upload_date:     datetime

    class Config:
        from_attributes = True


class ReportWithPatient(ReportOut):
    patient: Optional[PatientOut]

    class Config:
        from_attributes = True


class HistoryOut(BaseModel):
    id:            int
    patient_id:    int
    report_id:     int
    analysis_date: datetime
    patient:       Optional[PatientOut]
    report:        Optional[ReportOut]

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total_patients:  int
    total_reports:   int
    reports_today:   int
    recent_patients: List[PatientOut]
    recent_reports:  List[ReportOut]