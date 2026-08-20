import time
import logging
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from src.models import (
    IncomingSubmissionPayload,
    IngestionResponse,
    WorkflowStatus,
    StudentRequestDomainModel
)
from src.ingestion.idempotency import idempotency_cache
from src.core.ai_parser import RequestParserAgent
from src.core.rules_engine import RulesEngine
from src.notion.client import notion_client
from src.actions.email_service import EmailSender
from src.logging.run_logger import RunLogger

logger = logging.getLogger("campusdesk.ingestion")
router = APIRouter(prefix="/api/v1/requests", tags=["Ingestion & Workflow"])


@router.post("/submit", response_model=IngestionResponse, status_code=status.HTTP_201_CREATED)
async def submit_student_request(
    payload: IncomingSubmissionPayload,
    background_tasks: BackgroundTasks
):
    """
    Ingest a student request payload, deduplicate via SHA-256 idempotency hash,
    parse via Gemini 2.5 Flash, evaluate deterministic rules R1-R6, update Notion Control Center,
    and trigger automated real-world actions or human approval gates.
    """
    start_time = time.time()
    logger.info(f"Incoming Submission: Student='{payload.student_name}' | Email='{payload.contact_email}'")

    # 1. Idempotency Check & Hash Calculation
    req_hash = idempotency_cache.generate_hash(
        student_name=payload.student_name,
        raw_text=payload.raw_text,
        student_id=payload.student_id
    )

    existing_record = idempotency_cache.get(req_hash)
    if existing_record:
        logger.warning(f"Duplicate submission detected! ID={existing_record.request_id} | Hash={req_hash}")
        return IngestionResponse(
            status="success",
            duplicate_detected=True,
            request_id=existing_record.request_id,
            workflow_status=existing_record.status,
            message="Duplicate request received. Already registered in CampusDesk engine.",
            notion_url=existing_record.notion_url
        )

    # Generate Unique Request ID
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    short_suffix = uuid.uuid4().hex[:4].upper()
    request_id = f"REQ-{date_str}-{short_suffix}"

    # 2. AI Structuring (Gemini 2.5 Flash / Heuristic Fallback)
    parsed_ai = await RequestParserAgent.parse(payload.raw_text, payload.student_name, payload.student_id)
    logger.info(f"Parsed Request: Cat={parsed_ai.category.value} | Amt=₹{parsed_ai.requested_amount_inr} | Days={parsed_ai.duration_days} | Urgency={parsed_ai.urgency_level.value}")

    # 3. Dynamic Notion Rulebook Evaluation (Rules R1 - R6)
    dynamic_rulebook = await notion_client.fetch_dynamic_rulebook()
    decision = RulesEngine.evaluate(parsed_ai, dynamic_rulebook=dynamic_rulebook)
    logger.info(f"Rules Engine Decision: Status={decision.status.value} | Rule={decision.rule_id} | Reason='{decision.reason}'")

    # 4. Construct Domain Model
    domain_model = StudentRequestDomainModel(
        request_id=request_id,
        idempotency_hash=req_hash,
        student_name=payload.student_name or "Student",
        student_id=payload.student_id or "N/A",
        contact_email=payload.contact_email,
        category=parsed_ai.category,
        title=parsed_ai.title,
        summary=parsed_ai.summary,
        raw_text=payload.raw_text,
        amount_inr=parsed_ai.requested_amount_inr,
        duration_days=parsed_ai.duration_days,
        urgency=parsed_ai.urgency_level,
        status=decision.status,
        decision_reason=decision.reason
    )

    # 5. Notion Control Center Database Update
    page_id, page_url = await notion_client.create_request_page(domain_model)
    domain_model.notion_page_id = page_id
    domain_model.notion_url = page_url

    # Store in idempotency cache
    idempotency_cache.store(req_hash, domain_model)

    # 6. Process Workflow Action & Audit Logging
    if decision.status == WorkflowStatus.AUTO_APPROVED:
        msg = f"Request auto-approved by Rule {decision.rule_id}. PDF Certificate generated & emailed."
        action_desc = f"Auto-Approved (Rule: {decision.rule_id}) -> Dispatched Email & PDF"
        
        # Dispatch email asynchronously in background task to avoid HTTP timeout
        background_tasks.add_task(
            EmailSender.send_decision_email,
            domain_model,
            approver_notes="Auto-Approved by CampusDesk Rules Engine"
        )
    else:
        msg = f"Request ingested and paused at Notion Human Approval Gate (Rule {decision.rule_id}: {decision.reason})."
        action_desc = f"Workflow Paused at Notion Approval Gate (Rule: {decision.rule_id})"

    # Log run asynchronously in background task
    background_tasks.add_task(
        RunLogger.log_run,
        request_id=request_id,
        trigger_event="WEBHOOK_INGESTION",
        action_executed=action_desc,
        start_time_ms=start_time,
        success=True
    )

    return IngestionResponse(
        status="success",
        duplicate_detected=False,
        request_id=request_id,
        workflow_status=decision.status,
        message=msg,
        notion_url=page_url
    )
