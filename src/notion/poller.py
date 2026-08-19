import asyncio
import logging
import time
from src.notion.client import notion_client
from src.actions.email_service import EmailSender
from src.logging.run_logger import RunLogger
from src.models import WorkflowStatus

logger = logging.getLogger("campusdesk.poller")


class NotionGatePoller:
    """Background task long-polling Notion database for Human Approval Gate state transitions."""

    def __init__(self, poll_interval_seconds: int = 10):
        self.poll_interval_seconds = poll_interval_seconds
        self._running = False
        self._task: asyncio.Task = None

    async def start(self):
        """Start the background polling loop."""
        self._running = True
        self._task = asyncio.create_task(self._poll_loop())
        logger.info("Notion Human Approval Gate Poller started.")

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
        """Query Notion for pages moved to 'Approved' or 'Rejected' and execute pending actions."""
        pending_items = await notion_client.query_pending_approvals()
        
        for item in pending_items:
            start_time = time.time()
            page_id = item.get("id")
            status_text = item.get("status")
            domain_model = item.get("domain_model")

            if not domain_model or domain_model.action_executed:
                continue

            logger.info(f"Detected Human Approval Gate transition: Page {page_id} -> '{status_text}'")

            # Update status in domain model
            if status_text == "Approved":
                domain_model.status = WorkflowStatus.APPROVED
            elif status_text == "Rejected":
                domain_model.status = WorkflowStatus.REJECTED

            # 1. Execute Real-World Action (Send PDF & Email)
            email_success = await EmailSender.send_decision_email(domain_model, approver_notes="Approved via Notion Control Panel")
            domain_model.action_executed = True

            # 2. Programmatically log run in Notion Run Log
            action_msg = f"Human Gate Approved -> Sent PDF Certificate to {domain_model.contact_email}" if domain_model.status == WorkflowStatus.APPROVED else f"Human Gate Rejected -> Sent Notice to {domain_model.contact_email}"
            
            await RunLogger.log_run(
                request_id=domain_model.request_id,
                trigger_event="HUMAN_APPROVAL_GATE",
                action_executed=action_msg,
                start_time_ms=start_time,
                success=email_success
            )


# Global singleton instance
notion_poller = NotionGatePoller()
