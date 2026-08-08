# 🏥 MedScan AI — AI-Powered Medical Report Analyzer

<div align="center">

![MedScan AI](https://img.shields.io/badge/MedScan-AI-0d9488?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-LLaMA%204-F55036?style=for-the-badge)
![Render](https://img.shields.io/badge/Backend-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)
![Netlify](https://img.shields.io/badge/Frontend-Netlify-00C7B7?style=for-the-badge&logo=netlify&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)

**An intelligent full-stack medical report analyzer that reads X-rays, scans, and lab reports — then explains them in both clinical and plain-English terms using AI.**

[Live Demo](#-live-deployment) • [Features](#-features) • [Architecture](#-architecture) • [Setup](#-setup--installation) • [Run](#-running-the-app) • [API](#-api-reference)

</div>

---

## 🌐 Live Deployment

| Layer    | URL                                                                                     |
|----------|------------------------------------------------------------------------------------------|
| Frontend | [cheery-blancmange-f354e7.netlify.app](https://cheery-blancmange-f354e7.netlify.app)   |
| Backend  | [medscan-ai-5abm.onrender.com](https://medscan-ai-5abm.onrender.com)                   |
| API Docs | [medscan-ai-5abm.onrender.com/docs](https://medscan-ai-5abm.onrender.com/docs)         |
| Database | Aiven MySQL (Cloud, SSL-secured)                                                        |

> ⚠️ **Note:** The backend is hosted on Render's free tier — it may take **30–60 seconds to wake up** on first request after inactivity. Just wait and refresh.

---

## 📖 Overview

**MedScan AI** is a full-stack web application built during a 2-week AI & GPU Computing internship. It allows doctors to register patients, upload medical reports (PDF, JPG, PNG), and instantly receive AI-generated analysis — split into a **clinical summary** for doctors and a **plain-English summary** for patients.

Every user (doctor/staff/admin) has **fully isolated data** — your patients, reports, and history are visible only to you, while admins get a system-wide overview.

---

## ✨ Features

### 👤 Authentication & Users
- Secure registration & login with **JWT tokens**
- Passwords hashed with **bcrypt**
- Role-based access — **Admin / Doctor / Staff**
- Full profile page (name, DOB, specialization, hospital, activity log)

### 🧑‍⚕️ Patient Management
- Add, edit, delete, and search patients
- **Date of Birth** field with **auto-calculated age**
- Blood group, gender, phone, patient type (General/Emergency/Follow-up/Consultation)
- Per-doctor patient isolation

### 📄 Report Analysis (AI-Powered)
- Upload **PDF, JPG, or PNG** medical reports
- AI-generated structured report:
  - Key Findings
  - Abnormal Values (with normal ranges)
  - Normal Values
  - Clinical Impression
  - Recommendations
  - **Patient-Friendly Summary**
- Powered by **Groq API**:
  - Images → `LLaMA 4 Scout (Vision)`
  - PDFs → text extracted via `pdfplumber` → `LLaMA 3.3 70B`

### 📊 Dashboard
- Live stats: total patients, total reports, reports analyzed today
- Recent patients & recent reports
- Personal activity log

### 🛡️ Admin Panel
- View all registered users and their stats
- View all reports across all doctors
- Full audit visibility

### 📜 Analysis History
- Searchable history of all analyzed reports
- View full AI analysis anytime
- Delete with confirmation (dashboard updates live)

---

## 🏗️ Architecture

| Layer        | Technology                                |
|--------------|--------------------------------------------|
| Frontend     | HTML5, CSS3, Vanilla JavaScript            |
| Backend      | FastAPI, Python, Uvicorn                   |
| Database     | MySQL + SQLAlchemy ORM                     |
| Auth         | JWT (python-jose) + bcrypt (passlib)       |
| AI Engine    | Groq API — LLaMA 4 Scout (vision) & LLaMA 3.3 70B |
| File Parsing | pdfplumber (PDF text extraction)           |
| Hosting      | Render (backend) · Netlify (frontend) · Aiven (MySQL) |

---

## 📁 Project Structure

```
medscan-ai/
├── backend/
│   ├── main.py                # FastAPI app entrypoint
│   ├── database.py            # SQLAlchemy models & DB connection
│   ├── schemas.py             # Pydantic request/response schemas
│   ├── auth.py                # JWT + bcrypt utilities
│   ├── requirements.txt
│   ├── .env                   # Environment variables (not committed)
│   ├── .env.example           # Template for .env
│   └── routers/
│       ├── auth.py            # /auth/* endpoints
│       ├── patients.py        # /patients/* endpoints
│       ├── reports.py         # /reports/* endpoints
│       ├── analyze.py         # /analyze/* (Groq AI proxy)
│       └── dashboard.py       # /dashboard/* and /history/*
├── frontend/
│   └── index.html             # Complete single-file frontend
├── README.md
└── .gitignore
```

---

## ⚙️ Setup & Installation (Local)

### 1. Prerequisites
- Python 3.10+
- MySQL Server (running locally or remotely)
- A free [Groq API key](https://console.groq.com/keys)
- VS Code with **Live Server** extension (for frontend)

### 2. Clone the repository
```bash
git clone https://github.com/Deeksha-039/medscan-ai.git
cd medscan-ai
```

### 3. Create the MySQL database
```sql
CREATE DATABASE medscan_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. Configure environment variables
```bash
cd backend
cp .env.example .env
```
Edit `.env` and fill in your values:
```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=medscan_db
DB_USER=root
DB_PASSWORD=your_mysql_password

SECRET_KEY=your-secret-key-change-this
GROQ_API_KEY=your_groq_api_key_here
```

### 5. Install Python dependencies
```bash
pip install -r requirements.txt
```

---

## 🚀 Running the App (Local)

### Start the backend
```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
Backend will be running at `http://localhost:8000`  
API docs available at `http://localhost:8000/docs`

### Start the frontend
1. Open the `frontend/` folder in VS Code
2. Right-click `index.html` → **Open with Live Server**
3. The app opens at `http://127.0.0.1:5500/frontend/index.html`

### First-time use
1. Click **Register** → create a Doctor/Admin account (with name, DOB, email, password)
2. Login
3. Add a patient (Patient ID, name, DOB — age auto-calculates)
4. Go to **Upload Report** → search patient → upload PDF/JPG/PNG → **Analyze with AI**
5. View results in **Analysis History**

---

## ☁️ Deployment Guide

This app is deployed using three free-tier cloud services. Here's exactly how it's set up:

### 1. 🗄️ Database — Aiven MySQL

1. Create a free account at [aiven.io](https://aiven.io)
2. Create a new **MySQL** service (free tier)
3. Copy the connection details: host, port, user, password, database name
4. Enable **SSL** (required by Aiven — set `ssl_ca` or use `?ssl_disabled=False` in the connection URL)
5. Your `DATABASE_URL` will look like:
   ```
   mysql+pymysql://user:password@host:port/dbname?ssl_disabled=False
   ```

### 2. 🖥️ Backend — Render

1. Push your code to GitHub
2. Go to [render.com](https://render.com) → **New Web Service**
3. Connect your GitHub repo and select the `backend/` directory (or set root to `/`)
4. Set:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Under **Environment Variables**, add all keys from your `.env`:
   ```
   DB_HOST=your_aiven_host
   DB_PORT=your_aiven_port
   DB_NAME=defaultdb
   DB_USER=avnadmin
   DB_PASSWORD=your_aiven_password
   SECRET_KEY=your_secret_key
   GROQ_API_KEY=your_groq_key
   ```
6. Deploy — Render auto-deploys on every GitHub push
7. Your backend URL: `https://medscan-ai-5abm.onrender.com`

### 3. 🌐 Frontend — Netlify

1. Go to [netlify.com](https://netlify.com) → **Add new site → Deploy manually** (or connect GitHub)
2. Drag and drop the `frontend/` folder, OR connect repo and set **Publish directory** to `frontend`
3. **Important:** Make sure the API base URL in `index.html` points to your Render backend:
   ```javascript
   const API_BASE = "https://medscan-ai-5abm.onrender.com";
   ```
   (Not `localhost` — this was the most common deployment bug!)
4. Deploy → your frontend URL: `https://cheery-blancmange-f354e7.netlify.app`

### 4. ✅ CORS Setup

In `main.py`, ensure your Netlify URL is in the allowed origins:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://cheery-blancmange-f354e7.netlify.app",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🔌 API Reference

| Method | Endpoint              | Description                          | Auth |
|--------|------------------------|----------------------------------------|------|
| POST   | `/auth/register`       | Register new user                     | ❌   |
| POST   | `/auth/login`          | Login, returns JWT token              | ❌   |
| GET    | `/auth/me`             | Get current user profile              | ✅   |
| POST   | `/patients/`           | Create patient                        | ✅   |
| GET    | `/patients/`           | List patients (search/filter)         | ✅   |
| GET    | `/patients/{id}`       | Get single patient                    | ✅   |
| PUT    | `/patients/{id}`       | Update patient                        | ✅   |
| DELETE | `/patients/{id}`       | Delete patient                        | ✅   |
| POST   | `/reports/upload`      | Upload & store report                 | ✅   |
| GET    | `/reports/`            | List reports                          | ✅   |
| GET    | `/reports/{id}`        | Get single report                     | ✅   |
| DELETE | `/reports/{id}`        | Delete report                         | ✅   |
| POST   | `/analyze/`            | AI analysis via Groq (proxy)          | ✅   |
| GET    | `/dashboard/stats`     | Dashboard statistics                  | ✅   |
| GET    | `/history/`            | Analysis history                      | ✅   |
| DELETE | `/history/{id}`        | Delete history entry                  | ✅   |

Full interactive docs: [medscan-ai-5abm.onrender.com/docs](https://medscan-ai-5abm.onrender.com/docs)

---

## 🔐 Security Notes

- Never commit your `.env` file (already in `.gitignore`)
- Passwords are hashed using **bcrypt** — never stored in plain text
- All protected endpoints require a valid **JWT Bearer token**
- Per-user data isolation enforced at the database query level
- Aiven MySQL uses SSL — connection is encrypted in transit

---

## 🛣️ Roadmap

- [ ] EfficientNet-B4 CNN for local X-ray classification + Grad-CAM
- [ ] Fine-tuned BioMistral-7B for clinical NLP
- [ ] DICOM file support
- [ ] Mobile app (React Native)

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙋 Author

**Deeksha** — [github.com/Deeksha-039](https://github.com/Deeksha-039)

Built during an **AI & GPU Computing Internship** — 15-day program at NVIDIA × Presidency University covering ML fundamentals, CNNs, Transformers, LLM fine-tuning, and GPU optimization.
