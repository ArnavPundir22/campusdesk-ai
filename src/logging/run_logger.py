import uuid
import time
import logging
from src.notion.client import notion_client

logger = logging.getLogger("campusdesk.audit")


class RunLogger:
    """Programmatic audit run logger writing evidence to Notion System Run Log database."""

    @staticmethod
    async def log_run(
        request_id: str,
        trigger_event: str,
        action_executed: str,
        start_time_ms: float,
        success: bool = True
    ) -> str:
        execution_ms = int((time.time() - start_time_ms) * 1000)
        run_id = f"RUN-{time.strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"

        logger.info(f"Audit Log: {run_id} | Req: {request_id} | Event: {trigger_event} | Action: {action_executed} | Duration: {execution_ms}ms")

        try:
            return await notion_client.append_run_log(
                run_id=run_id,
                request_id=request_id,
                trigger_event=trigger_event,
                action_executed=action_executed,
                execution_ms=execution_ms,
                success=success
            )
        except Exception as e:
            logger.error(f"Failed to append to Notion Run Log: {e}")
            return run_id
