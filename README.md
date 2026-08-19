# CampusDesk AI 🎓⚡

**Autonomous Student Request & Approval Engine with Notion Operational Interface**

[![Notion Track](https://img.shields.io/badge/Track-Notion%20Automate%20India-000000?style=for-the-badge&logo=notion)](docs/PRD.md)
[![Backend](https://img.shields.io/badge/Backend-FastAPI%20%7C%20Python%203.11+-009688?style=for-the-badge&logo=fastapi)](docs/Architecture.md)
[![AI Engine](https://img.shields.io/badge/AI-Gemini%20%7C%20OpenAI-4285F4?style=for-the-badge&logo=google)](docs/Agents.md)

---

## 📌 Executive Overview

**CampusDesk AI** automates administrative workflows across college departments, academic offices, and student organizations. Incoming student requests (leave applications, event budget approvals, lab equipment borrowing) are parsed by AI, evaluated using deterministic Python business logic, and presented in Notion as styled operational cards for human review. High-stakes requests pause at a Human Approval Gate inside Notion and resume execution automatically once approved, generating official PDF documents and emailing stakeholders.

---

## 🏛️ Hackathon Judging Compliance Matrix

| Pillar | Requirement | How CampusDesk AI Satisfies It | Reference Docs |
|---|---|---|---|
| 1 | **Runs Unattended** | FastAPI background workers process incoming Webhook payloads with zero manual CLI steps. | [Architecture.md](docs/Architecture.md) |
| 2 | **Human-in-the-Loop Gate** | High-value requests (Budget > ₹1,000, multi-day leave) pause in Notion and poll for status changes. | [Rules.md](docs/Rules.md) |
| 3 | **Verifiable Audit Trail** | Programmatically writes timestamped execution records to the Notion `System Run Log` database. | [memory.md](docs/memory.md) |
| 4 | **Repository is the Engine** | Python code handles state, routing, and actions. Shutting down the repo stops external side-effects. | [SAD.md](docs/SAD.md) |
| 5 | **Human-Readable Notion Interface** | Formatted using callout boxes, toggle blocks, and status pills—never raw JSON dumps. | [design.md](docs/design.md) |

---

## 🏗️ System Architecture

```
+-----------------------------------------------------------------------------------+
|                                  EXTERNAL WORLD                                   |
|                                                                                   |
|   [Student Input] -----> [Webhook Ingestion API]                                  |
|                                   |                                               |
|                                   v                                               |
|                         +-------------------+                                     |
|                         |  FASTAPI BACKEND  |                                     |
|                         |  (Python Engine)  |                                     |
|                         +---------+---------+                                     |
|                                   |                                               |
|             +---------------------+---------------------+                         |
|             |                                           |                         |
|             v                                           v                         |
|    [External Actions]                         [Notion Integration]                |
|    - Resend / SMTP Email                      - Requests DB Sync                  |
|    - ReportLab PDF Generation                 - Human Approval Gate               |
|    - Webhook Dispatches                       - Programmatic Run Log              |
+-----------------------------------------------------------------------------------+
```

---

## 🤖 AI Agents & Deterministic Logic

CampusDesk AI separates unstructured text understanding from business execution:
* 🧠 **`RequestParserAgent`**: Converts unstructured multi-lingual emails, PDFs, or Hinglish text into strictly-typed Pydantic schemas.
* ⚙️ **`BusinessRulesEngine`**: Evaluates numeric thresholds and business logic in pure Python (`if amount > 1000: pause_for_approval()`).
* ✍️ **`ResponseDrafterAgent`**: Generates professional email copy and approval letters based on human decisions.

---

## 📂 Repository Structure

```
campusdesk-ai/
├── docs/                      # Complete Architecture & Requirement Specifications
│   ├── PRD.md                 # Product Requirements Document
│   ├── Architecture.md        # System Architecture & Flowcharts
│   ├── Agents.md              # AI Agent Specifications & Prompts
│   ├── SAD.md                 # Software Architecture Document
│   ├── TAD.md                 # Technical API & DB Schemas
│   ├── FAD.md                 # Functional Module Specifications
│   ├── FTL.md                 # Feature Traceability Matrix & Test Strategy
│   ├── Rules.md               # Business Rules & Judging Compliance Matrix
│   ├── design.md              # Notion UI & Block Formatting Specs
│   ├── phases.md              # Implementation Roadmap
│   └── memory.md              # Idempotency & State Management Architecture
├── README.md                  # Project Overview (This File)
└── .gitignore                 # Environment & Build Exclusions
```

---

## 🛠️ Tech Stack

* **Backend Framework:** Python 3.11+, FastAPI, Uvicorn
* **Database & Control Panel:** Notion REST API (v2022-06-28)
* **Structured AI Engine:** Google GenAI SDK / Instructor (Pydantic models)
* **Document Generation:** ReportLab
* **Email Service:** Resend API / SMTP

---

## 👤 Author & License

* **Developer:** [Arnav Pundir](https://github.com/ArnavPundir22)
* **License:** MIT License
