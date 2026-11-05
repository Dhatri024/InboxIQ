from fastapi import APIRouter, HTTPException
from models.request_models import EmailRequest
from services.ai_service import analyze_email_ai

router = APIRouter()

@router.post("/analyze")
def analyze_email(request: EmailRequest):

    text = request.text

    if not text.strip():
        raise HTTPException(status_code=422, detail="Email text cannot be empty.")

    tone = request.tone if request.tone else "formal"

    result = analyze_email_ai(text, tone)

    return result