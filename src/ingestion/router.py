import time
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, Header, BackgroundTasks
from src.models import (
    IncomingSubmissionPayload,
    StudentRequestDomainModel,
    WorkflowStatus
)
from src.ingestion.idempotency import idempotency_cache
from src.core.ai_parser import RequestParserAgent
from src.core.rules_engine import RulesEngine
from src.notion.client import notion_client
from src.actions.email_service import EmailSender
from src.logging.run_logger import RunLogger

router = APIRouter(prefix="/api/v1/requests", tags=["Student Requests Ingestion"])


@router.post("/submit", status_code=201)
async def submit_student_request(
    payload: IncomingSubmissionPayload,
    background_tasks: BackgroundTasks,
    x_idempotency_key: str = Header(default="")
):
    """Ingest incoming student request (Form JSON or Webhook), evaluate rules, sync to Notion, and dispatch actions."""
    start_time = time.time()

    # 1. Compute Idempotency Hash & Check Cache
    req_hash = idempotency_cache.generate_hash(
        student_name=payload.student_name,
        raw_text=payload.raw_text,
        student_id=payload.student_id
    )

    cached_record = idempotency_cache.get(req_hash)
    if cached_record:
        return {
            "status": "success",
            "duplicate_detected": True,
            "request_id": cached_record.request_id,
            "workflow_status": cached_record.status.value,
            "message": "Duplicate submission detected within 24h. Returned cached request state.",
            "notion_url": cached_record.notion_url
        }

    # 2. Generate Unique Request ID
    req_id = f"REQ-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"

    # 3. Step A: Structured AI Parsing
    parsed_req = await RequestParserAgent.parse(
        raw_text=payload.raw_text,
        student_name=payload.student_name,
        student_id=payload.student_id
    )

    # 4. Step B: Deterministic Business Rule Evaluation
    decision = RulesEngine.evaluate(parsed_req)

    # 5. Build Domain Model
    domain_model = StudentRequestDomainModel(
        request_id=req_id,
        idempotency_hash=req_hash,
        student_name=parsed_req.student_name,
        student_id=parsed_req.student_id,
        contact_email=payload.contact_email,
        category=parsed_req.category,
        title=parsed_req.title,
        summary=parsed_req.summary,
        raw_text=payload.raw_text,
        amount_inr=parsed_req.requested_amount_inr,
        duration_days=parsed_req.duration_days,
        urgency=parsed_req.urgency_level,
        status=decision.status,
        decision_reason=decision.reason
    )

    # 6. Step C: Create Notion Request Page
    page_id, page_url = await notion_client.create_request_page(domain_model)
    domain_model.notion_page_id = page_id
    domain_model.notion_url = page_url

    # Store in Idempotency Cache
    idempotency_cache.store(req_hash, domain_model)

    # 7. Action Branching
    if decision.status == WorkflowStatus.AUTO_APPROVED:
        # Execute Real Action immediately for auto-approved requests
        await EmailSender.send_decision_email(domain_model)
        domain_model.action_executed = True

        action_log = f"Auto-Approved (Rule: {decision.rule_id}) -> PDF Certificate generated & emailed to {payload.contact_email}"
        msg = f"Request auto-approved ({decision.reason}). Approval PDF sent to student email."
    else:
        # Paused at Notion Human Approval Gate
        action_log = f"Workflow Paused at Notion Approval Gate (Rule: {decision.rule_id})"
        msg = f"Request ingested and paused at Notion Human Approval Gate ({decision.reason})."

    # 8. Programmatic Notion Run Logging
    await RunLogger.log_run(
        request_id=req_id,
        trigger_event="WEBHOOK_INGESTION",
        action_executed=action_log,
        start_time_ms=start_time,
        success=True
    )

    return {
        "status": "success",
        "duplicate_detected": False,
        "request_id": req_id,
        "workflow_status": decision.status.value,
        "message": msg,
        "notion_url": page_url
    }
