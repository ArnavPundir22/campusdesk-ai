# PRD.md — Product Requirements Document
## Product Name: CampusDesk AI
**Subtitle:** Autonomous Student Request & Approval Engine with Notion Operational Interface
**Track:** Notion Track (Automate India Hackathon)

---

## 1. Problem Statement
Every college, department, and student organization in India deals with repetitive, manual administrative request workflows every single week:
* **The Chaos:** Student leave requests, event budget approvals, lab access applications, and equipment borrowing requests arrive as unstructured Google Form entries, PDFs, or raw messages in WhatsApp groups.
* **The Bottleneck:** Department coordinators and professors spend hours retyping details, manually emailing stakeholders for approvals, and manually updating spreadsheets. Requests frequently stall or get lost.
* **The Root Cause:** Administrative staff cannot code, and developers rarely build custom tools for specific college workflows. Off-the-shelf SaaS tools are too rigid or expensive.

---

## 2. Product Vision & Core Objective
**CampusDesk AI** automates the entire student request lifecycle cleanly:
* **The Code is the Engine:** A lightweight, self-hosted backend service (Python/FastAPI) ingests incoming student requests, parses messy text using structured AI models, validates business logic via code, routes high-stakes items for approval, executes real-world actions (sending official emails & generating PDFs), and programmatically updates Notion.
* **Notion is the Control Panel:** Notion serves as the human-readable database, operational dashboard, and audit trail. Professors and coordinators review human-readable request cards, approve/reject with a single click, and view live execution logs without ever opening a code repository.

---

## 3. Mandatory Hackathon Judging Pillars
CampusDesk AI strictly adheres to the 3 mandatory pillars of the Notion Track:

1. **Runs Unattended (Independent Service):**
   * Driven by webhook triggers (Form submission / API endpoint) and background workers.
   * Zero manual script executions required during live operations or demos.
2. **Human-in-the-Loop Approval inside Notion:**
   * High-stakes requests (e.g., budget requests > ₹1,000, multi-day leave, or lab equipment dispatch) pause execution.
   * Execution resumes *only* after a human updates the status in Notion from `Pending Approval` to `Approved` or `Rejected`.
3. **Leaves Verifiable Proof (Audit Trail):**
   * Every single run programmatically inserts a detailed, timestamped row into the Notion **Run Log** database.
   * Proof of execution is spread naturally across the event timeline with programmatic integration tokens (not manual entries).

---

## 4. Anti-Patterns & Explicit Non-Goals
To ensure maximum compliance with judging criteria, CampusDesk AI explicitly avoids:
* ❌ **No No-Code Zapier Chains:** The core engine lives in a version-controlled repository (`campusdesk-ai`). Deleting the repository stops the engine.
* ❌ **No Chatbots:** No conversational chat interface; chat is a doorway, not a workflow system.
* ❌ **No Passive Dashboards:** Real external side-effects occur (emails dispatched, PDF receipts generated, status webhooks sent).
* ❌ **No Raw JSON Dumps:** All Notion pages and database rows are formatted in clean, human-readable markdown with clear status tags and callout blocks.
* ❌ **No Superficial AI Overuse:** Deterministic rules handle validation (`if` statements); LLMs are strictly reserved for parsing unstructured text and drafting responses.

---

## 5. Key User Personas
1. **The Student (Requestor):** Submits requests via a simple web form or document upload; receives automated confirmation and final resolution notice.
2. **The Approver (Professor / Department Head):** Uses Notion on desktop/mobile to view parsed request summaries, click approval toggles, or override automated decisions.
3. **The Administrator / Auditor:** Views the Notion **Run Log** to monitor real-time system operations, failure alerts, and action history.

---

## 6. High-Level Feature Scope

| Feature Module | Description | Primary Interface |
|---|---|---|
| **Request Ingestion** | Ingests incoming form data, messy paragraphs, or PDF attachments via Webhook API. | FastAPI Backend |
| **Structured Parsing Engine** | Uses AI to parse unstructured text into standardized JSON schemas (Category, Urgency, Metadata). | Backend Logic + AI |
| **Deterministic Rule Evaluator** | Applies college business logic (e.g., auto-approve single-day leave if attendance > 75%, gate budget > ₹1,000 for HOD approval). | Backend Python Code |
| **Notion Control Center Sync** | Creates formatted Request cards and syncs state between backend and Notion. | Notion API |
| **Human Gate Monitor** | Long-polls or receives webhooks when a human updates a request status in Notion. | Notion Webhooks / Polling |
| **External Action Dispatcher** | Generates official PDF letters, sends emails via SMTP/Resend, and dispatches SMS/WhatsApp alerts. | External APIs |
| **Programmatic Run Logger** | Appends timestamped execution records to the Notion Run Log database. | Notion API |

---

## 7. Success Metrics & Definition of Done
* **100% Unattended Ingestion:** Webhook fires $\rightarrow$ Backend parses $\rightarrow$ Notion updates within $< 3$ seconds.
* **Human Control Test:** Turn off the backend service; the Notion workspace remains a structured, useful administrative hub.
* **Zero Lost Workflows:** Invalid or malformed inputs route automatically to human manual review rather than dropping silently.
* **Verifiable Run Log:** Every workflow step generates a programmatically signed Notion record.
