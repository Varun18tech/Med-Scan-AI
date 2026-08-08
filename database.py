from datetime import datetime
from sqlalchemy import (
    create_engine, Column, Integer, String,
    Text, DateTime, ForeignKey, Enum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST     = os.getenv("DB_HOST")
DB_PORT     = os.getenv("DB_PORT")
DB_NAME     = os.getenv("DB_NAME")
DB_USER     = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4&ssl_verify_cert=false"
)

engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id            = Column(Integer, primary_key=True, index=True)
    name          = Column(String(100), nullable=False)
    email         = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role          = Column(Enum("admin", "doctor", "staff"), default="staff")
    created_at    = Column(DateTime, default=datetime.utcnow)


class Patient(Base):
    __tablename__ = "patients"
    id           = Column(Integer, primary_key=True, index=True)
    patient_id   = Column(String(20), unique=True, nullable=False, index=True)
    name         = Column(String(150), nullable=False)
    age          = Column(Integer, nullable=False)
    gender       = Column(Enum("Male", "Female", "Other"), nullable=False)
    phone        = Column(String(20))
    patient_type = Column(
        Enum("General", "Emergency", "Follow-up", "Consultation"),
        default="General"
    )
    created_at   = Column(DateTime, default=datetime.utcnow)
    reports      = relationship("MedicalReport", back_populates="patient", cascade="all, delete")
    history      = relationship("AnalysisHistory", back_populates="patient", cascade="all, delete")


class MedicalReport(Base):
    __tablename__ = "medical_reports"
    id              = Column(Integer, primary_key=True, index=True)
    patient_id      = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"))
    file_name       = Column(String(255), nullable=False)
    file_type       = Column(String(10))
    original_text   = Column(Text)
    simple_summary  = Column(Text)
    medical_summary = Column(Text)
    upload_date     = Column(DateTime, default=datetime.utcnow)
    patient         = relationship("Patient", back_populates="reports")
    history         = relationship("AnalysisHistory", back_populates="report", cascade="all, delete")


class AnalysisHistory(Base):
    __tablename__ = "analysis_history"
    id            = Column(Integer, primary_key=True, index=True)
    patient_id    = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"))
    report_id     = Column(Integer, ForeignKey("medical_reports.id", ondelete="CASCADE"))
    analysis_date = Column(DateTime, default=datetime.utcnow)
    patient       = relationship("Patient", back_populates="history")
    report        = relationship("MedicalReport", back_populates="history")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    Base.metadata.create_all(bind=engine)
