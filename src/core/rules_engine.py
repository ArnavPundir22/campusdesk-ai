from typing import Dict, Any, Optional
from src.config import settings
from src.models import ParsedStudentRequest, WorkflowDecision, WorkflowStatus, RequestCategory


class RulesEngine:
    """Deterministic business rules engine evaluating student requests, supporting dynamic Notion Rulebook overrides."""

    @classmethod
    def evaluate(cls, parsed_req: ParsedStudentRequest, dynamic_rulebook: Optional[Dict[str, Dict[str, Any]]] = None) -> WorkflowDecision:
        category = parsed_req.category
        amount = parsed_req.requested_amount_inr
        days = parsed_req.duration_days
        rulebook = dynamic_rulebook or {}

        # 1. Budget Requests (Rule R2_BUDGET_THRESHOLD)
        if category == RequestCategory.BUDGET:
            rule_cfg = rulebook.get("R2_BUDGET_THRESHOLD", {})
            auto_enabled = rule_cfg.get("auto_approve", True)
            max_auto_budget = rule_cfg.get("max_budget", settings.AUTO_APPROVE_BUDGET_MAX_INR)

            if auto_enabled and 0.0 < amount <= max_auto_budget:
                return WorkflowDecision(
                    status=WorkflowStatus.AUTO_APPROVED,
                    requires_human_approval=False,
                    reason=f"Rule R2_BUDGET_THRESHOLD: Budget request (₹{amount:,.2f}) is within auto-approval threshold of ₹{max_auto_budget:,.2f}.",
                    rule_id="R2_BUDGET_THRESHOLD"
                )
            else:
                reason_detail = f"exceeds limit of ₹{max_auto_budget:,.2f}" if amount > max_auto_budget else "amount requires manual review"
                return WorkflowDecision(
                    status=WorkflowStatus.PENDING_APPROVAL,
                    requires_human_approval=True,
                    reason=f"Rule R2_BUDGET_THRESHOLD: Budget request (₹{amount:,.2f}) {reason_detail}; routed for HOD approval in Notion.",
                    rule_id="R2_BUDGET_THRESHOLD"
                )

        # 2. Student Leave Applications (Rule R3_LEAVE_THRESHOLD)
        if category == RequestCategory.LEAVE:
            rule_cfg = rulebook.get("R3_LEAVE_THRESHOLD", {})
            auto_enabled = rule_cfg.get("auto_approve", True)
            max_auto_days = int(rule_cfg.get("max_leave", settings.AUTO_APPROVE_LEAVE_MAX_DAYS))

            if auto_enabled and days <= max_auto_days:
                return WorkflowDecision(
                    status=WorkflowStatus.AUTO_APPROVED,
                    requires_human_approval=False,
                    reason=f"Rule R3_LEAVE_THRESHOLD: Leave application ({days} day) is within auto-approval threshold of {max_auto_days} day(s).",
                    rule_id="R3_LEAVE_THRESHOLD"
                )
            else:
                return WorkflowDecision(
                    status=WorkflowStatus.PENDING_APPROVAL,
                    requires_human_approval=True,
                    reason=f"Rule R3_LEAVE_THRESHOLD: Leave application ({days} days) exceeds limit ({max_auto_days} day); requires faculty approval in Notion.",
                    rule_id="R3_LEAVE_THRESHOLD"
                )

        # 3. Lab Equipment Borrowing (Rule R4_RESOURCE_GATE)
        if category == RequestCategory.LAB_EQUIPMENT:
            rule_cfg = rulebook.get("R4_RESOURCE_GATE", {})
            auto_enabled = rule_cfg.get("auto_approve", False)
            if auto_enabled:
                return WorkflowDecision(
                    status=WorkflowStatus.AUTO_APPROVED,
                    requires_human_approval=False,
                    reason="Rule R4_RESOURCE_GATE: Lab equipment request auto-approved by dynamic Notion rule policy.",
                    rule_id="R4_RESOURCE_GATE"
                )
            return WorkflowDecision(
                status=WorkflowStatus.PENDING_APPROVAL,
                requires_human_approval=True,
                reason="Rule R4_RESOURCE_GATE: Physical lab equipment and HPC borrowing requires lab coordinator verification.",
                rule_id="R4_RESOURCE_GATE"
            )

        # 4. Event Hall Bookings (Rule R5_EVENT_GATE)
        if category == RequestCategory.EVENT_HALL:
            rule_cfg = rulebook.get("R5_EVENT_GATE", {})
            auto_enabled = rule_cfg.get("auto_approve", False)
            if auto_enabled:
                return WorkflowDecision(
                    status=WorkflowStatus.AUTO_APPROVED,
                    requires_human_approval=False,
                    reason="Rule R5_EVENT_GATE: Event hall booking auto-approved by dynamic Notion rule policy.",
                    rule_id="R5_EVENT_GATE"
                )
            return WorkflowDecision(
                status=WorkflowStatus.PENDING_APPROVAL,
                requires_human_approval=True,
                reason="Rule R5_EVENT_GATE: Auditorium and seminar hall bookings require venue manager verification.",
                rule_id="R5_EVENT_GATE"
            )

        # 5. General Fallback (Rule R6_GENERAL_GATE)
        return WorkflowDecision(
            status=WorkflowStatus.PENDING_APPROVAL,
            requires_human_approval=True,
            reason="Rule R6_GENERAL_GATE: Unclassified general request routed for human administrative review.",
            rule_id="R6_GENERAL_GATE"
        )
