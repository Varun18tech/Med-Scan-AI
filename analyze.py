import base64
import os
from fastapi import APIRouter
from pydantic import BaseModel
from groq import Groq

router = APIRouter(prefix="/analyze", tags=["Analyze"])
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")


class AnalyzeRequest(BaseModel):
    file_base64: str
    file_type: str
    patient_name: str = ""
    patient_age: str = ""
    patient_gender: str = ""
    patient_dob: str = ""
    patient_blood: str = ""


@router.post("/")
async def analyze(body: AnalyzeRequest):
    try:
        client = Groq(api_key=GROQ_API_KEY)
        ext = body.file_type.lower()

        patient_info = f"""Patient Information:
Name: {body.patient_name}
Age: {body.patient_age}
Gender: {body.patient_gender}
DOB: {body.patient_dob}
Blood Group: {body.patient_blood}
"""

        if ext in ["jpg", "jpeg", "png"]:
            mime = "image/jpeg" if ext in ["jpg", "jpeg"] else "image/png"
            response = client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:{mime};base64,{body.file_base64}"}
                            },
                            {
                                "type": "text",
                                "text": f"""You are a senior consultant radiologist. Generate a formal professional radiology report for this medical image.

{patient_info}

Generate the report in this exact format:

================================
         RADIOLOGY REPORT
================================

PATIENT NAME      : {body.patient_name}
AGE               : {body.patient_age}
GENDER            : {body.patient_gender}
EXAMINATION TYPE  : [type of scan]
URGENCY           : [Routine / Semi-urgent / Urgent]

--------------------------------
CLINICAL INDICATION
--------------------------------
[Why this scan was likely done]

--------------------------------
FINDINGS
--------------------------------

LUNGS & AIRWAYS:
[Detailed findings]

HEART & MEDIASTINUM:
[Heart size, contour]

PLEURA:
[Effusion, pneumothorax, thickening]

BONES & SOFT TISSUES:
[Ribs, spine, soft tissue findings]

--------------------------------
IMPRESSION
--------------------------------
1.
2.

--------------------------------
RECOMMENDATIONS
--------------------------------
[Follow-up needed]

================================
        END OF REPORT
================================"""
                            }
                        ]
                    }
                ],
                max_tokens=2000
            )
            result = response.choices[0].message.content
            return {"medical_summary": result, "original_text": "[Image analyzed visually by AI]"}

        else:
            # PDF
            import io
            import pdfplumber
            pdf_bytes = base64.b64decode(body.file_base64)
            text = ""
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                text = "\n".join(page.extract_text() or "" for page in pdf.pages).strip()

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "user",
                        "content": f"""You are a senior consultant physician. Generate a formal professional medical report based on this report text.

{patient_info}

Report text:
{text}

Generate the report in the exact same hospital report format with sections: PATIENT INFO, CLINICAL INDICATION, FINDINGS, ABNORMAL VALUES, IMPRESSION, RECOMMENDATIONS."""
                    }
                ],
                max_tokens=2000
            )
            result = response.choices[0].message.content
            return {"medical_summary": result, "original_text": text}

    except Exception as e:
        return {"medical_summary": f"AI analysis error: {str(e)}", "original_text": ""}