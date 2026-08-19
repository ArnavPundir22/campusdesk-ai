# memory.md — State Management & Memory Architecture
## CampusDesk AI: System State, Persistence, & Idempotency Model

---

## 1. State Management & Memory Model
CampusDesk AI operates as a stateless event-driven service with persistent state mirrored across two layers:
1. **Local Persistent Cache (FastAPI SQLite / Redis):** Serves as an ephemeral operational cache for request deduplication, idempotency hashing, and status polling state.
2. **Notion Database (Source of Truth):** Serves as the durable state repository for human interaction, request lifecycle status, and operational run logs.

```
 +------------------+      1. Ingest       +-----------------------+
 | Student Request  | -------------------> | FastAPI Ingestion API |
 +------------------+                      +-----------+-----------+
                                                       |
                                           2. Check Hash / Store
                                                       v
                                           +-----------------------+
                                           |  State Cache (SQLite) |
                                           +-----------+-----------+
                                                       |
                                            3. Sync State / Write
                                                       v
                                           +-----------------------+
                                           |    Notion Database    |
                                           |  (Durable Truth)      |
                                           +-----------------------+
```

---

## 2. Idempotency & Deduplication Strategy
To guarantee zero duplicate submissions or duplicate emails when a student clicks submit multiple times:
* Every incoming payload is hashed using SHA-256 (`SHA256(student_id + category + amount + timestamp_date)`).
* Before processing, the backend queries the local state cache. If the hash exists and was processed within the last 24 hours, the backend returns the existing `Request ID` and HTTP 200 without creating a duplicate row in Notion or re-triggering emails.

---

## 3. Notion Run Log Schema & Audit Provenance

Every step in the workflow writes a programmatic row to the Notion **Run Log** database.

### 3.1 Run Log Item Data Schema
* **Run ID:** `RUN-20260819-9942`
* **Request Reference:** `REQ-20260819-A8F1`
* **Trigger Event:** `WEBHOOK_INGESTION` | `HUMAN_APPROVAL_GATE` | `ACTION_DISPATCH`
* **Action Executed:** `PDF Certificate Generated & Dispatched to aarav.sharma@university.edu.in`
* **Execution Duration:** `1,240 ms`
* **Timestamp:** `2026-08-19T22:10:00Z`
* **Success:** `True`

---

## 4. Session Context & Recovery Protocols
* **System Restart Recovery:** If the FastAPI backend service restarts or crashes, the background poller reads the Notion `Student Requests` database on boot, identifies any `Approved` or `Rejected` items that have not yet been marked as `Action Executed`, and processes them automatically. Zero state is lost on server crash.
