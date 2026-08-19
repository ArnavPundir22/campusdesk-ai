from src.config import settings
from src.models import ParsedStudentRequest, WorkflowDecision, WorkflowStatus, RequestCategory


class RulesEngine:
    """Deterministic business rules engine evaluating student requests."""

    @staticmethod
    def evaluate(parsed_req: ParsedStudentRequest) -> WorkflowDecision:
        category = parsed_req.category
        amount = parsed_req.requested_amount_inr
        days = parsed_req.duration_days

        # Rule 1 & 2: Financial Reimbursements
        if category == RequestCategory.BUDGET:
            max_auto_budget = settings.AUTO_APPROVE_BUDGET_MAX_INR
            if amount <= max_auto_budget:
                return WorkflowDecision(
                    status=WorkflowStatus.AUTO_APPROVED,
                    requires_human_approval=False,
                    reason=f"Rule R1: Budget request (₹{amount:,.2f}) is within auto-approval threshold of ₹{max_auto_budget:,.2f}.",
                    rule_id="R1_BUDGET_AUTO"
                )
            else:
                return WorkflowDecision(
                    status=WorkflowStatus.PENDING_APPROVAL,
                    requires_human_approval=True,
                    reason=f"Rule R2: Budget request (₹{amount:,.2f}) exceeds auto-approval limit (₹{max_auto_budget:,.2f}); routed for HOD approval.",
                    rule_id="R2_BUDGET_GATE"
                )

        # Rule 3 & 4: Student Leave Applications
        if category == RequestCategory.LEAVE:
            max_auto_days = settings.AUTO_APPROVE_LEAVE_MAX_DAYS
            if days <= max_auto_days:
                return WorkflowDecision(
                    status=WorkflowStatus.AUTO_APPROVED,
                    requires_human_approval=False,
                    reason=f"Rule R3: Single-day emergency leave ({days} day) auto-approved.",
                    rule_id="R3_LEAVE_AUTO"
                )
            else:
                return WorkflowDecision(
                    status=WorkflowStatus.PENDING_APPROVAL,
                    requires_human_approval=True,
                    reason=f"Rule R4: Multi-day leave application ({days} days) requires faculty advisor approval.",
                    rule_id="R4_LEAVE_GATE"
                )

        # Rule 5: Lab Equipment & Facilities Dispatch
        if category in (RequestCategory.LAB_EQUIPMENT, RequestCategory.EVENT_HALL):
            return WorkflowDecision(
                status=WorkflowStatus.PENDING_APPROVAL,
                requires_human_approval=True,
                reason=f"Rule R5: Physical resource dispatch ({category.value}) requires lab coordinator verification.",
                rule_id="R5_RESOURCE_GATE"
            )

        # Rule 6: General / Fallback
        return WorkflowDecision(
            status=WorkflowStatus.PENDING_APPROVAL,
            requires_human_approval=True,
            reason="Rule R6: Default policy; unclassified request routed for human administrative review.",
            rule_id="R6_DEFAULT_GATE"
        )
