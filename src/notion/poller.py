import asyncio
import logging
import time
from src.notion.client import notion_client
from src.actions.email_service import EmailSender
from src.logging.run_logger import RunLogger
from src.models import StudentRequestDomainModel, WorkflowStatus, RequestCategory, UrgencyLevel

logger = logging.getLogger("campusdesk.poller")


class NotionGatePoller:
    """Background task long-polling Notion database for Human Approval Gate state transitions."""

    def __init__(self, poll_interval_seconds: int = 3):
        self.poll_interval_seconds = poll_interval_seconds
        self._running = False
        self._task: asyncio.Task = None
        self._processed_page_ids = set()

    async def start(self):
        """Start the background polling loop."""
        self._running = True
        self._task = asyncio.create_task(self._poll_loop())
        logger.info(f"Notion Human Approval Gate Poller started (Interval: {self.poll_interval_seconds}s).")

    async def stop(self):
        """Stop the background polling loop."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Notion Human Approval Gate Poller stopped.")

    async def _poll_loop(self):
        while self._running:
            try:
                await self.check_approval_gate_transitions()
            except Exception as e:
                logger.error(f"Error in Notion poller iteration: {e}")
            await asyncio.sleep(self.poll_interval_seconds)

    async def check_approval_gate_transitions(self):
        """Query Notion for pages moved to 'Approved' or 'Rejected' by human approvers."""
        pending_items = await notion_client.query_pending_approvals()
        
        for item in pending_items:
            start_time = time.time()
            
            # 1. Live Notion Page Object
            if isinstance(item, dict) and "properties" in item:
                page_id = item.get("id")
                if page_id in self._processed_page_ids:
                    continue

                props = item.get("properties", {})
                status_obj = props.get("Status", {}).get("select") or {}
                status_text = status_obj.get("name", "")

                if status_text not in ("Approved", "Rejected"):
                    continue

                # Lock immediately to prevent duplicate async dispatches
                self._processed_page_ids.add(page_id)

                # Extract Properties
                req_id_list = props.get("Request ID", {}).get("title", [])
                req_id = req_id_list[0].get("text", {}).get("content", "") if req_id_list else "REQ-UNKNOWN"

                student_name_list = props.get("Student Name", {}).get("rich_text", [])
                s_name = student_name_list[0].get("text", {}).get("content", "Student") if student_name_list else "Student"

                summary_list = props.get("AI Reasoning Summary", {}).get("rich_text", [])
                summary_text = summary_list[0].get("text", {}).get("content", "") if summary_list else ""

                amount = props.get("Amount (INR)", {}).get("number") or 0.0
                cat_name = props.get("Category", {}).get("select", {}).get("name", "GENERAL")

                try:
                    category_enum = RequestCategory(cat_name)
                except ValueError:
                    category_enum = RequestCategory.GENERAL

                workflow_status = WorkflowStatus.APPROVED if status_text == "Approved" else WorkflowStatus.REJECTED

                domain_model = StudentRequestDomainModel(
                    request_id=req_id,
                    idempotency_hash="live_notion_sync",
                    student_name=s_name,
                    student_id="",
                    contact_email="abhivanshrana22@gmail.com",
                    category=category_enum,
                    title=f"Request {req_id}",
                    summary=summary_text,
                    raw_text=summary_text,
                    amount_inr=amount,
                    duration_days=1,
                    urgency=UrgencyLevel.MEDIUM,
                    status=workflow_status,
                    decision_reason=f"Approved by Department Head in Notion Control Center"
                )

                logger.info(f"⚡ Live Notion Gate Transition Detected: Page {page_id} [{req_id}] -> '{status_text}'")

                # Dispatch PDF Approval Certificate & Email
                email_success = await EmailSender.send_decision_email(
                    domain_model,
                    approver_notes=f"Processed via Notion Control Center ({status_text})"
                )

                # Log run to Notion System Run Log
                action_msg = f"Human Gate {status_text} -> PDF Certificate generated & dispatched"
                await RunLogger.log_run(
                    request_id=req_id,
                    trigger_event="HUMAN_APPROVAL_GATE",
                    action_executed=action_msg,
                    start_time_ms=start_time,
                    success=email_success
                )

            # 2. Mock Page Object
            elif isinstance(item, dict) and "domain_model" in item:
                page_id = item.get("id")
                if page_id in self._processed_page_ids:
                    continue

                status_text = item.get("status")
                domain_model = item.get("domain_model")

                if not domain_model or domain_model.action_executed:
                    continue

                self._processed_page_ids.add(page_id)

                if status_text == "Approved":
                    domain_model.status = WorkflowStatus.APPROVED
                elif status_text == "Rejected":
                    domain_model.status = WorkflowStatus.REJECTED

                email_success = await EmailSender.send_decision_email(domain_model, approver_notes="Approved via Notion Control Panel")
                domain_model.action_executed = True

                action_msg = f"Human Gate Approved -> Sent PDF Certificate" if domain_model.status == WorkflowStatus.APPROVED else f"Human Gate Rejected"
                await RunLogger.log_run(
                    request_id=domain_model.request_id,
                    trigger_event="HUMAN_APPROVAL_GATE",
                    action_executed=action_msg,
                    start_time_ms=start_time,
                    success=email_success
                )


# Global singleton instance
notion_poller = NotionGatePoller()
