# Agents.md — AI Agent Specifications & Tool Contracts
## CampusDesk AI: Autonomous Student Request & Approval Engine

---

## 1. Executive Summary & Design Constraints
In accordance with **Notion Track Rule #4 ("Where AI Actually Earns Its Place")**:
* **Rule of Thumb:** *"If an `if` statement could have done it, an `if` statement should have done it."*
* AI is strictly scoped to unstructured tasks: parsing messy input text/PDFs, categorizing request semantics, and drafting professional approval/rejection copy.
* Hard validation, numeric threshold evaluation, database writes, and email dispatches are executed by **deterministic Python backend code**.

---

## 2. Agent Inventory & Roles

CampusDesk AI utilizes two specialized agent pipelines:

```
                  +-----------------------------------+
                  |   INCOMING UNSTRUCTURED REQUEST   |
                  +-----------------+-----------------+
                                    |
                                    v
                  +-----------------------------------+
                  |      1. REQUEST PARSER AGENT      |
                  |   (Text/PDF -> Structured JSON)   |
                  +-----------------+-----------------+
                                    |
                                    v
                  +-----------------------------------+
                  |    PYTHON BUSINESS LOGIC ENGINE   |
                  |     (Determines Auto vs Gate)     |
                  +-----------------+-----------------+
                                    |
                                    v
                  +-----------------------------------+
                  |     2. RESPONSE DRAFTER AGENT     |
                  |   (Generates Professional Copy)   |
                  +-----------------------------------+
```

---

## 3. Agent Specifications

### 3.1 Agent #1: Request Parser Agent (`RequestParserAgent`)
* **Purpose:** Convert messy, multi-lingual, or unstructured student text submissions into a strictly typed Pydantic schema.
* **Model Configuration:** Gemini 1.5 Flash (or GPT-4o-mini) with `response_mime_type="application/json"`.
* **Input:** Raw text string, extracted PDF OCR text, or email body.
* **Output Schema (Pydantic):**

```python
from pydantic import BaseModel, Field
from typing import Optional, List

class ParsedStudentRequest(BaseModel):
    student_name: str = Field(description="Full name of the requesting student")
    student_id: str = Field(description="Roll number or student ID if present")
    category: str = Field(description="One of: LEAVE, BUDGET_REIMBURSEMENT, LAB_EQUIPMENT, EVENT_HALL, GENERAL")
    title: str = Field(description="Concise 5-8 word title summarizing the request")
    summary: str = Field(description="2-3 sentence executive summary of the request")
    urgency_level: str = Field(description="LOW, MEDIUM, HIGH, or CRITICAL based on dates mentioned")
    requested_amount_inr: Optional[float] = Field(default=0.0, description="Financial reimbursement amount in INR if applicable")
    duration_days: Optional[int] = Field(default=1, description="Number of leave/borrowing days requested")
    key_entities: List[str] = Field(default_factory=list, description="Extracted dates, department names, or equipment codes")
    reasoning_for_category: str = Field(description="Brief explanation of why this category was assigned")
```

* **System Prompt:**
  ```text
  You are an expert academic administrative assistant for an Indian university.
  Your task is to parse incoming unstructured student requests into a precise JSON schema.
  Rules:
  1. Never hallucinate missing student IDs; if not provided, leave empty string.
  2. Extract numeric values carefully (e.g., 'five hundred rupees' -> 500.0).
  3. If text is written in Hindi/Hinglish or regional languages, translate the summary into clear English while preserving key details.
  4. Output MUST conform strictly to the JSON schema.
  ```

---

### 3.2 Agent #2: Response Drafter Agent (`ResponseDrafterAgent`)
* **Purpose:** Generate professional, polite, and contextual email copy and approval letters based on the human approver's decision or automated approval rules.
* **Input:** Parsed Request Object + Decision Status (`APPROVED` / `REJECTED`) + Approver Notes.
* **Output Schema (Pydantic):**

```python
class DraftedResponse(BaseModel):
    email_subject: str = Field(description="Official email subject line including Request ID")
    email_body_html: str = Field(description="Clean, HTML-formatted email response for the student")
    pdf_letter_content: str = Field(description="Formal text to embed into the generated approval PDF")
```

* **System Prompt:**
  ```text
  You draft official university correspondence.
  Create a clear, polite, and professional email response and PDF certificate text.
  Include the Request ID, student name, decision status, and any specific notes provided by the department head.
  ```

---

## 4. Fallback & Safety Mechanisms
* **JSON Validation Failure:** If LLM output fails Pydantic validation after 2 retry attempts, the backend automatically flags the request as `PARSE_ERROR` and routes the raw text to Notion under **"Manual Processing Required"** with a `HIGH` urgency tag. No data is lost.
* **Language Translation Guard:** Indian student submissions written in mixed Hinglish (e.g. *"Sir emergency leave chahiye for brother wedding from 12th to 14th"*) are translated to formal English while retaining original dates.
