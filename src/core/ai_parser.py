import re
import logging
from typing import Optional
from src.config import settings
from src.models import ParsedStudentRequest, RequestCategory, UrgencyLevel

logger = logging.getLogger("campusdesk.parser")


class RequestParserAgent:
    """AI Agent responsible for parsing unstructured student text into structured JSON models."""

    SYSTEM_PROMPT = """You are an expert academic administrative assistant for an Indian university.
Your task is to parse incoming unstructured student requests into a precise JSON schema.

Rules:
1. Never hallucinate missing student IDs; if not provided in raw text, leave empty string.
2. Extract numeric amounts carefully (e.g. 'fifteen hundred rupees' -> 1500.0, 'Rs 1,450' -> 1450.0).
3. Identify leave durations (e.g. '2 days leave' -> duration_days=2).
4. Assign category from: LEAVE, BUDGET, LAB_EQUIPMENT, EVENT_HALL, GENERAL.
5. If text is in Hindi/Hinglish, translate summary into formal English while retaining key dates and names.
6. Provide a concise 5-8 word title and 2-3 sentence executive summary.
"""

    @classmethod
    async def parse(cls, raw_text: str, student_name: str = "", student_id: str = "") -> ParsedStudentRequest:
        """Parse raw text input using Gemini API or fallback heuristic parser."""
        # Try Gemini API if key is valid
        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "mock_key":
            try:
                return await cls._parse_with_gemini(raw_text, student_name, student_id)
            except Exception as e:
                logger.warning(f"Gemini API parse failed: {e}. Falling back to heuristic parser.")

        # Heuristic fallback parser
        return cls._parse_heuristic(raw_text, student_name, student_id)

    @classmethod
    async def _parse_with_gemini(cls, raw_text: str, student_name: str, student_id: str) -> ParsedStudentRequest:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        prompt = f"Student Name: {student_name}\nStudent ID: {student_id}\nRaw Request:\n{raw_text}"

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[cls.SYSTEM_PROMPT, prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ParsedStudentRequest,
                temperature=0.1
            ),
        )

        return ParsedStudentRequest.model_validate_json(response.text)

    @classmethod
    def _parse_heuristic(cls, raw_text: str, student_name: str = "", student_id: str = "") -> ParsedStudentRequest:
        """Deterministic regex and keyword parser for offline, mock, and test environments."""
        text_lower = raw_text.lower()

        # Category detection
        category = RequestCategory.GENERAL
        if any(w in text_lower for w in ["leave", "sick", "absent", "chutti", "casual leave", "wedding"]):
            category = RequestCategory.LEAVE
        elif any(w in text_lower for w in ["reimbursement", "budget", "rs", "rupees", "inr", "cost", "receipt", "purchase", "amount", "spent", "₹"]):
            category = RequestCategory.BUDGET
        elif any(w in text_lower for w in ["equipment", "lab", "sensor", "arduino", "microscope", "oscilloscope", "component"]):
            category = RequestCategory.LAB_EQUIPMENT
        elif any(w in text_lower for w in ["auditorium", "hall", "event", "venue", "seminar"]):
            category = RequestCategory.EVENT_HALL

        # Amount extraction (e.g. Rs 1,450, 1450 rupees, ₹1450, Rs. 500)
        amount = 0.0
        amount_match = re.search(r'(?:rs\.?|rupees|inr|₹)\s*([\d,]+(?:\.\d+)?)|([\d,]+(?:\.\d+)?)\s*(?:rs\.?|rupees|inr|₹)', text_lower)
        if amount_match:
            val_str = amount_match.group(1) or amount_match.group(2)
            try:
                amount = float(val_str.replace(",", ""))
            except ValueError:
                amount = 0.0

        # Duration days extraction (e.g. 2 days, 3-day, one day, single day)
        days = 1
        days_match = re.search(r'(\d+)\s*(?:day|days)', text_lower)
        if days_match:
            try:
                days = int(days_match.group(1))
            except ValueError:
                days = 1
        elif "multi-day" in text_lower or "two days" in text_lower or "three days" in text_lower:
            days = 2

        # Urgency detection
        urgency = UrgencyLevel.MEDIUM
        if any(w in text_lower for w in ["urgent", "emergency", "immediately", "today", "critical"]):
            urgency = UrgencyLevel.HIGH

        # Title & Summary construction
        s_name = student_name or "Student"
        title = f"{category.value.replace('_', ' ').title()} Request from {s_name}"
        summary = f"{s_name} submitted a {category.value.lower()} request. Details extracted: '{raw_text[:120]}...'."

        return ParsedStudentRequest(
            student_name=student_name or "Student",
            student_id=student_id,
            category=category,
            title=title,
            summary=summary,
            urgency_level=urgency,
            requested_amount_inr=amount,
            duration_days=days,
            key_entities=[category.value],
            reasoning_for_category=f"Heuristic parser assigned {category.value} based on text patterns."
        )
