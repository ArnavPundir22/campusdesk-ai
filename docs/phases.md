# phases.md — Implementation Roadmap & Milestones
## CampusDesk AI: Development Phases

---

## Phase Overview

```
+-----------------------------------------------------------------------------------+
| PHASE 1: Notion Workspace & Database Foundation                                   |
| - Create Notion Databases (Student Requests, Run Log, Approvals Queue)            |
| - Generate Notion Integration Secret Token & Obtain DB IDs                        |
+-----------------------------------------------------------------------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------------+
| PHASE 2: Core Backend Engine & AI Parsing                                         |
| - Implement FastAPI server endpoints (`/requests/submit`)                         |
| - Build `RequestParserAgent` (Pydantic structured output with Gemini/OpenAI)     |
| - Implement deterministic `RulesEngine` for Auto-Approval vs Human-Gate decisions |
+-----------------------------------------------------------------------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------------+
| PHASE 3: Notion Sync & Human-in-the-Loop Gate                                     |
| - Build Notion API Client (`notion/client.py`) & Block Formatter (`formatter.py`) |
| - Implement background poller for Human Approval Gate status changes             |
| - Implement programmatic Run Logger (`logging/run_logger.py`)                     |
+-----------------------------------------------------------------------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------------+
| PHASE 4: Real External Actions & Hardening                                        |
| - Implement ReportLab PDF Approval Certificate Generator                          |
| - Implement Resend/SMTP Email Dispatcher                                          |
| - Write automated pytest suite & verify end-to-end flow                           |
+-----------------------------------------------------------------------------------+
```

---

## Phase Breakdown & Deliverables

### Phase 1: Workspace & Integration Setup
- [x] Set up project repository `campusdesk-ai`.
- [x] Create Notion Databases (`Student Requests`, `System Run Log`).
- [x] Configure environment secrets in `.env`.

### Phase 2: Ingestion & Engine Development
- [x] Construct FastAPI server and request payload schemas.
- [x] Implement AI structured parsing (`RequestParserAgent`).
- [x] Code deterministic business rules (`rules_engine.py`).

### Phase 3: Notion Sync & Gate Polling
- [x] Implement programmatic creation of human-readable Notion cards.
- [x] Implement async status polling for human approval changes in Notion.
- [x] Implement timestamped Notion Run Log logging.

### Phase 4: Action Execution & End-to-End Testing
- [x] Build ReportLab PDF certificate generation service.
- [x] Integrate Resend/SMTP email dispatcher.
- [x] Run full verification test suite (`pytest tests/`).
