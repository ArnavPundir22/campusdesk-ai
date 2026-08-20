from enum import Enum
from datetime import datetime, timezone
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field

class RequestCategory(str, Enum):
    LEAVE = "LEAVE"
    BUDGET = "BUDGET"
    LAB_EQUIPMENT = "LAB_EQUIPMENT"
    EVENT_HALL = "EVENT_HALL"
    GENERAL = "GENERAL"


class WorkflowStatus(str, Enum):
    DRAFT = "DRAFT"
    AUTO_APPROVED = "AUTO_APPROVED"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PARSE_ERROR = "PARSE_ERROR"


class UrgencyLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class IncomingSubmissionPayload(BaseModel):
    student_name: str = Field(description="Full name of student requestor")
    student_id: str = Field(default="", description="Roll number or student ID")
    contact_email: str = Field(description="Email address for notification and PDF delivery")
    raw_text: str = Field(description="Unstructured student request text")
    department: Optional[str] = Field(default="", description="Department or school name")


class IngestionResponse(BaseModel):
    status: str = Field(default="success")
    duplicate_detected: bool = Field(default=False)
    request_id: str = Field(description="Unique request ID REQ-YYYYMMDD-XXXX")
    workflow_status: WorkflowStatus
    message: str
    notion_url: Optional[str] = None



class ParsedStudentRequest(BaseModel):
    student_name: str = Field(description="Full name of requesting student")
    student_id: str = Field(default="", description="Roll number or student ID")
    category: RequestCategory = Field(description="Assigned request category")
    title: str = Field(description="Concise 5-8 word title summarizing request")
    summary: str = Field(description="2-3 sentence executive summary")
    urgency_level: UrgencyLevel = Field(default=UrgencyLevel.MEDIUM, description="Assigned urgency level")
    requested_amount_inr: float = Field(default=0.0, description="Financial amount in INR if applicable")
    duration_days: int = Field(default=1, description="Number of leave/borrowing days requested")
    key_entities: List[str] = Field(default_factory=list, description="Extracted dates, departments, or item codes")
    reasoning_for_category: str = Field(default="", description="Reasoning for assigned category")


class WorkflowDecision(BaseModel):
    status: WorkflowStatus
    requires_human_approval: bool
    reason: str
    rule_id: str


class StudentRequestDomainModel(BaseModel):
    request_id: str = Field(description="Unique string ID: REQ-YYYYMMDD-XXXX")
    idempotency_hash: str
    student_name: str
    student_id: str
    contact_email: str
    category: RequestCategory
    title: str
    summary: str
    raw_text: str
    amount_inr: float = 0.0
    duration_days: int = 1
    urgency: UrgencyLevel = UrgencyLevel.MEDIUM
    status: WorkflowStatus
    decision_reason: str = ""
    notion_page_id: Optional[str] = None
    notion_url: Optional[str] = None
    action_executed: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DraftedResponse(BaseModel):
    email_subject: str = Field(description="Official email subject line")
    email_body_html: str = Field(description="HTML formatted email body")
    pdf_letter_content: str = Field(description="Formal approval letter text for PDF rendering")


class RunLogEntry(BaseModel):
    run_id: str = Field(description="Unique run ID: RUN-YYYYMMDD-XXXX")
    request_id: str
    trigger_event: str
    action_executed: str
    execution_time_ms: int
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    success: bool = True
    details: Optional[Dict[str, Any]] = None
