import pytest
from src.core.ai_parser import RequestParserAgent
from src.models import RequestCategory


@pytest.mark.asyncio
async def test_heuristic_parser_budget():
    raw_text = "Sir requesting reimbursement of Rs 850 spent on purchasing Arduino sensors for Robotics Competition"
    parsed = await RequestParserAgent.parse(raw_text, student_name="Aarav Sharma", student_id="2023-CS-042")
    
    assert parsed.category == RequestCategory.BUDGET
    assert parsed.requested_amount_inr == 850.0
    assert parsed.student_name == "Aarav Sharma"
    assert parsed.student_id == "2023-CS-042"


@pytest.mark.asyncio
async def test_heuristic_parser_leave():
    raw_text = "Respected Ma'am, emergency leave required for 3 days due to brother wedding from 12th to 14th."
    parsed = await RequestParserAgent.parse(raw_text, student_name="Rhea Kapoor")

    assert parsed.category == RequestCategory.LEAVE
    assert parsed.duration_days == 3
    assert parsed.student_name == "Rhea Kapoor"
