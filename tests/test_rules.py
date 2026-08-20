from src.core.rules_engine import RulesEngine
from src.models import ParsedStudentRequest, RequestCategory, WorkflowStatus, UrgencyLevel


def test_rule_budget_under_threshold_auto_approved():
    parsed = ParsedStudentRequest(
        student_name="Aarav Sharma",
        category=RequestCategory.BUDGET,
        title="Arduino Sensors",
        summary="Buying sensors for robotics",
        requested_amount_inr=850.0
    )
    decision = RulesEngine.evaluate(parsed)
    assert decision.status == WorkflowStatus.AUTO_APPROVED
    assert decision.requires_human_approval is False
    assert decision.rule_id == "R2_BUDGET_THRESHOLD"


def test_rule_budget_over_threshold_requires_approval():
    parsed = ParsedStudentRequest(
        student_name="Aarav Sharma",
        category=RequestCategory.BUDGET,
        title="Laptop Reimbursement",
        summary="Purchased high-end component",
        requested_amount_inr=4500.0
    )
    decision = RulesEngine.evaluate(parsed)
    assert decision.status == WorkflowStatus.PENDING_APPROVAL
    assert decision.requires_human_approval is True
    assert decision.rule_id == "R2_BUDGET_THRESHOLD"


def test_rule_leave_single_day_auto_approved():
    parsed = ParsedStudentRequest(
        student_name="Rhea Kapoor",
        category=RequestCategory.LEAVE,
        title="1-Day Emergency Leave",
        summary="Emergency leave for family event",
        duration_days=1
    )
    decision = RulesEngine.evaluate(parsed)
    assert decision.status == WorkflowStatus.AUTO_APPROVED
    assert decision.requires_human_approval is False
    assert decision.rule_id == "R3_LEAVE_THRESHOLD"


def test_rule_leave_multiday_requires_approval():
    parsed = ParsedStudentRequest(
        student_name="Rhea Kapoor",
        category=RequestCategory.LEAVE,
        title="3-Day Leave",
        summary="Attending outstation conference",
        duration_days=3
    )
    decision = RulesEngine.evaluate(parsed)
    assert decision.status == WorkflowStatus.PENDING_APPROVAL
    assert decision.requires_human_approval is True
    assert decision.rule_id == "R3_LEAVE_THRESHOLD"


def test_rule_lab_equipment_always_requires_approval():
    parsed = ParsedStudentRequest(
        student_name="Karan Patel",
        category=RequestCategory.LAB_EQUIPMENT,
        title="Oscilloscope Borrowing",
        summary="Borrowing oscilloscope for 1 day",
        duration_days=1
    )
    decision = RulesEngine.evaluate(parsed)
    assert decision.status == WorkflowStatus.PENDING_APPROVAL
    assert decision.requires_human_approval is True
    assert decision.rule_id == "R4_RESOURCE_GATE"


def test_dynamic_notion_rulebook_override():
    """Test that dynamic Notion Rulebook configuration overrides default limits."""
    parsed = ParsedStudentRequest(
        student_name="Aarav Sharma",
        category=RequestCategory.BUDGET,
        title="Project Expense",
        summary="Reimbursement of Rs 2500",
        requested_amount_inr=2500.0
    )
    
    # Dynamic Notion Rulebook setting Max Auto Budget to 3000
    dynamic_rulebook = {
        "R2_BUDGET_THRESHOLD": {
            "auto_approve": True,
            "max_budget": 3000.0,
            "max_leave": 0
        }
    }
    
    decision = RulesEngine.evaluate(parsed, dynamic_rulebook=dynamic_rulebook)
    assert decision.status == WorkflowStatus.AUTO_APPROVED
    assert decision.requires_human_approval is False
