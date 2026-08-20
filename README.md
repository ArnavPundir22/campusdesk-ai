# CampusDesk AI 🎓⚡

**Autonomous Student Request & Approval Engine with Notion Operational Interface**

[![Live Cloud Server](https://img.shields.io/badge/Render-Live%2024%2F7-22c55e?style=for-the-badge&logo=render)](https://campusdesk-ai.onrender.com)
[![Notion Track](https://img.shields.io/badge/Track-Notion%20Automate%20India-000000?style=for-the-badge&logo=notion)](docs/PRD.md)
[![Backend](https://img.shields.io/badge/Backend-FastAPI%20%7C%20Python%203.11+-009688?style=for-the-badge&logo=fastapi)](docs/Architecture.md)
[![AI Engine](https://img.shields.io/badge/AI-Gemini%202.5%20Flash-4285F4?style=for-the-badge&logo=google)](docs/Agents.md)

---

## 🌐 Live Production Links & Forms

* 🚀 **Live Cloud Server URL**: **[https://campusdesk-ai.onrender.com](https://campusdesk-ai.onrender.com)**
* 📝 **Live Google Form Submission**: **[https://forms.gle/xLJWQrskbwez9CkK8](https://forms.gle/xLJWQrskbwez9CkK8)**
* 🎨 **Live Visual Student Request Portal**: **[https://campusdesk-ai.onrender.com/form](https://campusdesk-ai.onrender.com/form)**
* ⚡ **Live Webhook Endpoint**: `https://campusdesk-ai.onrender.com/api/v1/requests/submit`
* 💚 **System Health Check**: **[https://campusdesk-ai.onrender.com/health](https://campusdesk-ai.onrender.com/health)**
* 📋 **Google Forms Setup Guide & Script**: **[docs/GoogleFormsSetup.md](docs/GoogleFormsSetup.md)**
* 📖 **Render Deployment Blueprint & Guide**: **[docs/RenderDeployment.md](docs/RenderDeployment.md)**

---

> [!IMPORTANT]
> ### ✉️ Email Delivery & Testing Note
> Currently, the system uses **Resend API in Test Mode** (`onboarding@resend.dev`). Under Resend's free tier rules, testing emails with PDF attachments are delivered **exclusively to the registered owner's email address (`abhivanshrana22@gmail.com`)**.  
> Additionally, every generated PDF Approval Certificate is saved locally on disk inside the [`pdf_certificates/`](file:///home/dell/campusdesk-ai/pdf_certificates/) folder for immediate review!  
> *(To deliver emails to any external student domain e.g. `@university.edu.in`, verify a custom domain under [resend.com/domains](https://resend.com/domains) and update `SENDER_EMAIL` in `.env`.)*

---

## 📌 Executive Overview

**CampusDesk AI** automates administrative workflows across college departments, academic offices, and student organizations. Incoming student requests (leave applications, event budget approvals, lab equipment borrowing) are parsed by **Gemini 2.5 Flash**, evaluated using deterministic Python business logic, and presented in Notion as styled operational cards for human review. High-stakes requests pause at a Human Approval Gate inside Notion and resume execution automatically once approved, generating official PDF documents and emailing stakeholders.

---

## 📖 Dynamic Notion Rulebook

CampusDesk AI features a **Live Dynamic Rulebook Database** in Notion! Administrators can modify auto-approval thresholds, budget limits, or rule toggles directly inside Notion without writing code:

| Rule ID | Category | Auto Approve Enabled | Max Auto Budget (INR) | Max Auto Leave Days | Rule Description |
|---|---|---|---|---|---|
| **`R2_BUDGET_THRESHOLD`** | `BUDGET` | `[x]` | **`₹1,000`** | `0` | Budget requests under threshold auto-approved. |
| **`R3_LEAVE_THRESHOLD`** | `LEAVE` | `[x]` | `0` | **`1 Day`** | Single-day leave auto-approved. |
| **`R4_RESOURCE_GATE`** | `LAB_EQUIPMENT` | `[ ]` | `0` | `0` | Physical lab equipment requires verification. |
| **`R5_EVENT_GATE`** | `EVENT_HALL` | `[ ]` | `0` | `0` | Venue booking requires manager approval. |
| **`R6_GENERAL_GATE`** | `GENERAL` | `[ ]` | `0` | `0` | Uncategorized requests pause for human review. |

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
|   [Student Input] -----> [Google Form / Web Portal Webhook]                        |
|                                   |                                               |
|                                   v                                               |
|                         +-------------------+                                     |
|                         |  FASTAPI BACKEND  |                                     |
|                         |  (Render Cloud)   |                                     |
|                         +---------+---------+                                     |
|                                   |                                               |
|             +---------------------+---------------------+                         |
|             |                                           |                         |
|             v                                           v                         |
|    [External Actions]                         [Notion Integration]                |
|    - Resend API Email                         - Requests DB Sync                  |
|    - ReportLab PDF Generation                 - Human Approval Gate               |
|    - Local PDF Certificate Storage            - Dynamic Rulebook Sync             |
|    - Webhook Dispatches                       - Programmatic Run Log              |
+-----------------------------------------------------------------------------------+
```

---

## 📂 Repository Structure

```
campusdesk-ai/
├── docs/                      # Architecture & Requirement Specifications
│   ├── PRD.md                 # Product Requirements Document
│   ├── Architecture.md        # System Architecture & Flowcharts
│   ├── GoogleFormsSetup.md    # Google Forms Integration Guide & Apps Script Code
│   ├── RenderDeployment.md    # Render Cloud Infrastructure Setup Guide
│   ├── Agents.md              # AI Agent Specifications & Prompts
│   ├── SAD.md                 # Software Architecture Document
│   ├── TAD.md                 # Technical API & DB Schemas
│   ├── FAD.md                 # Functional Module Specifications
│   ├── Rules.md               # Business Rules & Judging Compliance Matrix
│   ├── design.md              # Notion UI & Block Formatting Specs
│   └── memory.md              # Idempotency & State Management Architecture
├── src/                       # Production Engine Codebase
├── templates/                 # Student Request Web Portal (form.html)
├── pdf_certificates/          # Local PDF Approval Certificates Storage
├── render.yaml                # Render Infrastructure Blueprint
├── Procfile                   # Cloud Process Launcher
└── README.md                  # Project Overview (This File)
```

---

## 🛠️ Tech Stack

* **Backend Framework:** Python 3.11+, FastAPI, Uvicorn (Deployed on Render Cloud 24/7)
* **Database & Control Panel:** Notion REST API (v2022-06-28)
* **Structured AI Engine:** Google GenAI SDK (Gemini 2.5 Flash) with 3s Timeout & Regex Fallback
* **Document Generation:** ReportLab PDF Engine
* **Email Service:** Resend API (Owner Email Testing Mode: `abhivanshrana22@gmail.com`)

---

## 👤 Author & License

* **Developer:** [Arnav Pundir](https://github.com/ArnavPundir22)
* **License:** MIT License
