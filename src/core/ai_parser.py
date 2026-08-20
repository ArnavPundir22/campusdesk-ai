import re
import logging
import asyncio
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
        """Parse raw text input using Gemini API with fast 3s timeout or instant fallback heuristic parser."""
        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "mock_key":
            try:
                # Wrap Gemini call in 3.0s timeout to prevent API rate-limit delays
                return await asyncio.wait_for(
                    cls._parse_with_gemini(raw_text, student_name, student_id),
                    timeout=3.0
                )
            except Exception as e:
                logger.warning(f"Gemini API parse bypassed ({e}). Using high-speed heuristic fallback parser.")

        # Heuristic fallback parser (instant <1ms response)
        return cls._parse_heuristic(raw_text, student_name, student_id)

    @classmethod
    async def _parse_with_gemini(cls, raw_text: str, student_name: str, student_id: str) -> ParsedStudentRequest:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        prompt = f"Student Name: {student_name}\nStudent ID: {student_id}\nRaw Request Text:\n{raw_text}"

        response = client.models.generate_content(
            model=settings.AI_MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=cls.SYSTEM_PROMPT,
                response_mime_type="application/json",
                response_schema=ParsedStudentRequest,
                temperature=0.1
            )
        )
        return ParsedStudentRequest.model_validate_json(response.text)

    @classmethod
    def _parse_heuristic(cls, raw_text: str, student_name: str = "", student_id: str = "") -> ParsedStudentRequest:
        """Deterministic regex and keyword parser for instant offline / rate-limited processing."""
        text_lower = raw_text.lower()
        category = RequestCategory.GENERAL
        requested_amount_inr = 0.0
        duration_days = 1
        urgency_level = UrgencyLevel.MEDIUM

        # 1. Extract Financial Amounts
        amount_matches = re.findall(r'(?:rs\.?|inr|₹|\brupees\b)\s*([\d,]+(?:\.\d+)?)|([\d,]+)\s*(?:rs|inr|rupees)', text_lower)
        if amount_matches:
            for match in amount_matches:
                val_str = (match[0] or match[1]).replace(",", "")
                try:
                    requested_amount_inr = float(val_str)
                    category = RequestCategory.BUDGET
                    break
                except ValueError:
                    pass

        # 2. Extract Leave Durations
        day_matches = re.findall(r'(\d+)\s*(?:day|days)\b', text_lower)
        if day_matches:
            try:
                duration_days = int(day_matches[0])
                if category == RequestCategory.GENERAL:
                    category = RequestCategory.LEAVE
            except ValueError:
                pass
        elif any(k in text_lower for k in ["leave", "absent", "fever", "sick", "vacation", "permission to absent"]):
            if category == RequestCategory.GENERAL:
                category = RequestCategory.LEAVE

        # 3. Detect Specific Categories (Priority: Reimbursement/Budget > Hall > Lab Borrowing)
        if any(k in text_lower for k in ["reimbursement", "budget", "grant", "expense", "bill", "purchasing"]):
            category = RequestCategory.BUDGET
        elif any(k in text_lower for k in ["hall", "auditorium", "seminar", "venue", "booking", "stage", "sound"]):
            category = RequestCategory.EVENT_HALL
        elif any(k in text_lower for k in ["oscilloscope", "component", "kit", "hpc", "borrow", "access hpc"]):
            category = RequestCategory.LAB_EQUIPMENT

        # 4. Detect Urgency
        if any(k in text_lower for k in ["urgent", "emergency", "immediate", "today", "asap"]):
            urgency_level = UrgencyLevel.HIGH

        title = f"{category.value.title().replace('_', ' ')} Request for {student_name or 'Student'}"
        summary = f"Student {student_name or 'Student'} ({student_id or 'ID N/A'}) submitted a {category.value} request. Raw text: '{raw_text[:150]}...'"

        return ParsedStudentRequest(
            student_name=student_name,
            student_id=student_id,
            category=category,
            title=title,
            summary=summary,
            urgency_level=urgency_level,
            requested_amount_inr=requested_amount_inr,
            duration_days=duration_days,
            key_entities=[],
            reasoning_for_category="Parsed via heuristic offline parser."
        )
