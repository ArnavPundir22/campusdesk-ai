# SAD.md — Software Architecture Document
## CampusDesk AI: Autonomous Student Request & Approval Engine

---

## 1. High-Level Software Package Structure

```
campusdesk-ai/
├── docs/                      # Architectural & Requirements Documentation
│   ├── PRD.md
│   ├── Architecture.md
│   ├── Agents.md
│   ├── FAD.md
│   ├── FTL.md
│   ├── SAD.md
│   ├── TAD.md
│   ├── Rules.md
│   ├── phases.md
│   ├── design.md
│   └── memory.md
├── src/                       # Core Python Application Code
│   ├── __init__.py
│   ├── main.py                # FastAPI Application & Server Entrypoint
│   ├── config.py              # Environment Variables & Settings (Pydantic Settings)
│   ├── ingestion/             # Ingestion Layer
│   │   ├── __init__.py
│   │   ├── router.py          # REST API Endpoints
│   │   └── idempotency.py     # Request Hashing & Deduplication
│   ├── core/                  # Engine & AI Logic
│   │   ├── __init__.py
│   │   ├── ai_parser.py       # LLM Parser Agent Interface
│   │   ├── response_drafter.py# LLM Email/PDF Copy Drafter
│   │   └── rules_engine.py    # Deterministic Business Logic Evaluator
│   ├── notion/                # Notion Integration
│   │   ├── __init__.py
│   │   ├── client.py          # Async Notion REST API Client
│   │   ├── formatter.py       # Rich Markdown/Block Component Builder
│   │   └── poller.py          # Background Human Approval Gate Poller
│   ├── actions/               # External Action Execution
│   │   ├── __init__.py
│   │   ├── pdf_engine.py      # ReportLab Dynamic PDF Generation
│   │   └── email_service.py   # Resend/SMTP Email Dispatcher
│   └── logging/               # Audit & Run Logging
│       ├── __init__.py
│       └── run_logger.py      # Programmatic Notion Run Log Writer
├── templates/                 # PDF & Email Templates
│   └── approval_letter.html
├── tests/                     # Automated Test Suites
│   ├── conftest.py
│   ├── test_parser.py
│   ├── test_rules.py
│   └── test_integration.py
├── .env.example               # Environment Configuration Blueprint
├── requirements.txt           # Production Python Dependencies
└── README.md                  # Project Quickstart & Setup Guide
```

---

## 2. Technology Selection Rationale

| Layer | Selected Tech | Justification |
|---|---|---|
| **Backend Runtime** | Python 3.11+ | Native support for AI libraries, async/await HTTP servers, and rich document generation. |
| **API Framework** | FastAPI | High-performance async ASGI web framework with automatic OpenAPI documentation and input validation. |
| **Database & UI** | Notion API | Fully satisfies Notion Track requirements for database, human control panel, and audit logging. |
| **AI LLM Framework** | Google GenAI / Instructor | Enforces strict JSON schema validation and structured outputs for LLMs. |
| **PDF Generation** | ReportLab | Lightweight Python library for programmatically rendering vector-quality PDF approval certificates. |
| **Email Dispatch** | Resend API / SMTP | Zero-friction HTTP/SMTP email service for real-world side effects. |

---

## 3. Data Models & Interface Contracts

### 3.1 Core Request Domain Model (`src/core/models.py`)
```python
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

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

class StudentRequestDomainModel(BaseModel):
    request_id: str = Field(description="Unique UUID string: REQ-YYYYMMDD-XXXX")
    idempotency_hash: str
    student_name: str
    student_id: str
    category: RequestCategory
    title: str
    summary: str
    amount_inr: float = 0.0
    duration_days: int = 1
    urgency: str = "MEDIUM"
    status: WorkflowStatus
    notion_page_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
```
