# FTL.md — Feature Traceability & Testing Lifecycle
## CampusDesk AI: Autonomous Student Request & Approval Engine

---

## 1. Feature Traceability Matrix (FTM)
This matrix maps every hackathon requirement and product feature directly to its software module, API interface, and verification test case.

| Requirement ID | Requirement Description | Implementation Module | Source File | Verification Test |
|---|---|---|---|---|
| **REQ-01** | System must run unattended via Webhook/Cron without manual script execution. | Ingestion & Background Worker | `src/ingestion/webhook.py` | `test_unattended_webhook_flow()` |
| **REQ-02** | High-stakes workflows must pause and wait for human approval in Notion. | Notion Gate Poller | `src/notion/poller.py` | `test_human_approval_gate()` |
| **REQ-03** | Every execution must write a timestamped row to the Notion Run Log. | Audit Logger | `src/logging/run_logger.py` | `test_run_log_provenance()` |
| **REQ-04** | AI must handle unstructured messy inputs (multilingual/PDF/paragraphs). | Request Parser Agent | `src/core/ai_parser.py` | `test_messy_input_parsing()` |
| **REQ-05** | System must perform a real external action (Email / PDF generation). | Action Dispatcher | `src/actions/pdf_email.py` | `test_pdf_and_email_dispatch()` |
| **REQ-06** | System must gracefully handle invalid/corrupted inputs without crashing. | Error Handler & Fallback | `src/core/error_handler.py` | `test_malformed_input_fallback()` |
| **REQ-07** | Deleting repository stops engine (Proves code is the engine, not no-code). | Service Architecture | Root Repo Architecture | Automated test suite verification |

---

## 2. Testing Strategy & Test Cases

### 2.1 Test Suite 1: Automated Integration Tests (`tests/test_integration.py`)
Run via Pytest:
```bash
pytest tests/ -v --tb=short
```

1. **`test_auto_approval_flow`**:
   - **Scenario:** Single-day leave request submitted via Webhook.
   - **Expected Result:** Status set to `AUTO_APPROVED`, PDF generated, Email sent, Run Log entry written to Notion in $<2.5$ seconds.
2. **`test_human_gated_flow`**:
   - **Scenario:** Budget request for ₹5,000 submitted.
   - **Expected Result:** Status set to `PENDING_APPROVAL`, row created in Notion Approvals Queue, no email sent yet. When simulated status change to `APPROVED` occurs, backend fires action and writes final Run Log row.
3. **`test_duplicate_prevention`**:
   - **Scenario:** Identical request payload sent twice within 10 seconds.
   - **Expected Result:** Second request detected by idempotency hash; returns HTTP 200 with existing Request ID; zero duplicate Notion rows created.

### 2.2 Test Suite 2: Resilience & Chaos Tests (`tests/test_resilience.py`)
1. **`test_malformed_pdf_input`**:
   - Ingests a corrupt binary file. Checks that system routes to Notion **"Manual Review Required"** database with high urgency tag instead of crashing with HTTP 500.
2. **`test_notion_api_downtime_retry`**:
   - Simulates Notion API rate limit (HTTP 429). Checks that exponential backoff retry mechanism attempts 3 retries before logging warning.
