# Rules.md — Business & Compliance Rules
## CampusDesk AI: Operational & Judging Compliance Matrix

---

## 1. Hackathon Judging Rules Compliance Matrix
This document establishes strict adherence to every requirement outlined in the official Notion Track brief.

```
+---------------------------------------------------------------------------------------+
|                                JUDGING PILLARS MATRIX                                 |
+--------------------------+----------------------------------+-------------------------+
| HACKATHON REQUIREMENT    | COMPLIANCE METHOD                | VERIFICATION MECHANISM  |
+--------------------------+----------------------------------+-------------------------+
| 1. Runs Unattended       | FastApi webhook + async background| Automated HTTP webhook  |
|                          | workers on deployed host.         | ingestion without manual|
|                          | Zero manual script triggers.     | CLI calls.              |
+--------------------------+----------------------------------+-------------------------+
| 2. Human Approval Gate   | High-risk workflows pause and    | Notion UI Status field  |
|                          | wait in Notion for human update. | polling & execution     |
|                          |                                  | hold verification.      |
+--------------------------+----------------------------------+-------------------------+
| 3. Verifiable Run Log    | Code writes timestamped rows to  | Programmatic Notion token|
|                          | Notion Run Log for every step.   | attribution check.      |
+--------------------------+----------------------------------+-------------------------+
| 4. Delete Repo Test      | System engine strictly lives in  | Turning off backend     |
|                          | Python repository (`campusdesk`).| stops automated actions.|
+--------------------------+----------------------------------+-------------------------+
| 5. Human Readability     | Rich Notion blocks, callouts, and| Workspace evaluation by |
|                          | clear status tags (no raw JSON). | human judges.           |
+--------------------------+----------------------------------+-------------------------+
```

---

## 2. Strict Anti-Pattern Enforcement

CampusDesk AI explicitly enforces the following architectural bans:

1. **NO NO-CODE MIDDLEWARE BANS:**
   - **Rule:** Zapier, Make, and N8n canvas chains are prohibited.
   - **Enforcement:** All ingestion, parsing, rule evaluation, Notion synchronization, and action dispatches are written in native Python modules (`src/`).
2. **NO CHATBOT DOORWAYS:**
   - **Rule:** Conversational Q&A chatbots are prohibited.
   - **Enforcement:** The system is an asynchronous event-driven workflow engine, not a conversational assistant.
3. **NO RAW MODEL JSON DUMPING:**
   - **Rule:** Model JSON dumps must never be pasted raw into Notion pages.
   - **Enforcement:** `src/notion/formatter.py` transforms all internal schemas into beautifully styled Notion blocks (Callout boxes, Bullet Lists, Styled Status Badges).
4. **NO AI OVERUSE ("IF STATEMENT" RULE):**
   - **Rule:** If an `if` statement can evaluate logic, an `if` statement MUST evaluate it.
   - **Enforcement:** Numeric thresholds, leave duration calculations, and status transitions are governed strictly by deterministic `if/else` logic in `src/core/rules_engine.py`.

---

## 3. Academic Business Logic Rules

The backend engine applies the following deterministic business rules (`src/core/rules_engine.py`):

```python
# Business Logic Rules Hierarchy

# Rule 1: Financial Reimbursements
IF Category == "BUDGET":
    IF Amount_INR <= 1000.0:
        Decision = AUTO_APPROVED
        Reason = "Budget request under auto-approval threshold of ₹1,000"
    ELSE:
        Decision = REQUIRES_HUMAN_APPROVAL
        Reason = "High-value budget request (₹1,000+) requires HOD approval"

# Rule 2: Student Leave Applications
IF Category == "LEAVE":
    IF Duration_Days <= 1:
        Decision = AUTO_APPROVED
        Reason = "Single day emergency leave auto-approved"
    ELSE:
        Decision = REQUIRES_HUMAN_APPROVAL
        Reason = "Multi-day leave application requires faculty approval"

# Rule 3: Lab Equipment & Facilities
IF Category IN ["LAB_EQUIPMENT", "EVENT_HALL"]:
    Decision = REQUIRES_HUMAN_APPROVAL
    Reason = "Physical resource dispatch requires staff verification"
```
