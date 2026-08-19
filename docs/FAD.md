# FAD.md — Functional Architecture Document
## CampusDesk AI: Autonomous Student Request & Approval Engine

---

## 1. Functional Module Architecture
CampusDesk AI is structured into six distinct functional modules:

```
  +-----------------------------------------------------------------------+
  |                           CAMPUSDESK ENGINE                           |
  |                                                                       |
  |  +---------------------+       +-----------------------------------+  |
  |  | 1. Ingestion Module | ----> | 2. AI Parsing & Structuring       |  |
  |  +---------------------+       +-----------------------------------+  |
  |                                                  |                    |
  |                                                  v                    |
  |  +---------------------+       +-----------------------------------+  |
  |  | 4. Notion Control   | <---- | 3. Business Rules Engine          |  |
  |  |    Sync & Polling   |       +-----------------------------------+  |
  |  +---------------------+                         |                    |
  |             | (Human Gate)                       | (Auto-Approved)    |
  |             v                                    v                    |
  |  +-----------------------------------------------------------------+  |
  |  | 5. Action Execution Module (PDF / Email / Webhook)              |  |
  |  +-----------------------------------------------------------------+  |
  |                                    |                                  |
  |                                    v                                  |
  |  +-----------------------------------------------------------------+  |
  |  | 6. Audit & Run Logging Module (Programmatic Notion Run Log)     |  |
  |  +-----------------------------------------------------------------+  |
  +-----------------------------------------------------------------------+
```

---

## 2. Module Functional Specifications

### 2.1 Module 1: Ingestion Module (`src/ingestion`)
* **Functionality:** Accepts incoming requests from multiple digital entry points.
* **Supported Inputs:**
  - `POST /api/v1/requests/submit` (JSON Payload from custom HTML Web Form).
  - `POST /api/v1/requests/webhook` (Generic Webhook receiver).
  - Direct file upload endpoint for PDFs / images.
* **Key Functions:**
  - `ingest_raw_request(payload: dict) -> RawRequest`
  - `generate_idempotency_hash(payload: dict) -> str`

### 2.2 Module 2: AI Parsing & Structuring (`src/core/parser.py`)
* **Functionality:** Ingests raw unstructured text/PDFs, calls the `RequestParserAgent`, and emits a validated `ParsedStudentRequest` data model.
* **Key Functions:**
  - `parse_unstructured_input(raw_text: str) -> ParsedStudentRequest`
  - `retry_on_parse_error(max_retries: int = 2)`

### 2.3 Module 3: Business Rules Engine (`src/core/rules.py`)
* **Functionality:** Pure deterministic Python evaluation of business thresholds without LLM involvement.
* **Logic Rules:**
  - Rule R1: If Category = `LEAVE` AND Days $\le 1$ $\rightarrow$ `AUTO_APPROVED`
  - Rule R2: If Category = `LEAVE` AND Days $> 1$ $\rightarrow$ `REQUIRES_HUMAN_APPROVAL`
  - Rule R3: If Category = `BUDGET` AND Amount $\le ₹1,000$ $\rightarrow$ `AUTO_APPROVED`
  - Rule R4: If Category = `BUDGET` AND Amount $> ₹1,000$ $\rightarrow$ `REQUIRES_HUMAN_APPROVAL`
  - Rule R5: If Category = `LAB_EQUIPMENT` $\rightarrow$ Always `REQUIRES_HUMAN_APPROVAL`
* **Key Functions:**
  - `evaluate_rules(parsed_req: ParsedStudentRequest) -> RuleDecision`

### 2.4 Module 4: Notion Control Sync & Polling (`src/notion`)
* **Functionality:** Manages bidirection communication with Notion workspace.
* **Functions:**
  - `create_notion_request_page(parsed_req, decision) -> str` (Returns Notion Page ID)
  - `poll_pending_approvals() -> List[NotionStatusUpdate]`
  - `format_notion_blocks(parsed_req) -> List[dict]`

### 2.5 Module 5: Action Execution Module (`src/actions`)
* **Functionality:** Executes external side-effects in the physical world.
* **Outputs:**
  - Generates formal PDF certificate (`PDFGenerator.create_approval_letter()`).
  - Sends HTML email with attached PDF (`EmailSender.send_decision_email()`).
  - Triggers external notification webhook (`WebhookDispatcher.fire()`).

### 2.6 Module 6: Audit & Run Logging Module (`src/logging`)
* **Functionality:** Writes immutable, timestamped execution evidence to Notion.
* **Key Functions:**
  - `log_run_event(run_id, request_id, action_taken, execution_ms, status)`
