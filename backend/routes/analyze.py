from fastapi import APIRouter
from models.request_models import EmailRequest
from services.ai_service import analyze_email_ai

router = APIRouter()

@router.post("/analyze")
def analyze_email(request: EmailRequest):

    text = request.text
    tone = request.tone if request.tone else "formal"

    result = analyze_email_ai(text, tone)

    return result