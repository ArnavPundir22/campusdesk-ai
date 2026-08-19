# TAD.md — Technical Architecture Document
## CampusDesk AI: Autonomous Student Request & Approval Engine

---

## 1. API Specifications & Endpoints

### 1.1 Ingestion Endpoints (`src/ingestion/router.py`)

#### Endpoint 1: Submit Request (Form / JSON)
* **HTTP Method:** `POST /api/v1/requests/submit`
* **Content-Type:** `application/json` or `multipart/form-data`
* **Request Headers:**
  - `X-Idempotency-Key`: Optional unique client string.
* **Request Body (JSON Example):**
  ```json
  {
    "student_name": "Aarav Sharma",
    "student_id": "2023-CS-042",
    "raw_text": "Sir, requesting reimbursement of Rs 1,450 spent on purchasing Arduino sensors for the Robotics Competition held on 15th Aug.",
    "contact_email": "aarav.sharma@university.edu.in"
  }
  ```
* **Response Payload (HTTP 201 Created):**
  ```json
  {
    "status": "success",
    "request_id": "REQ-20260819-A8F1",
    "workflow_status": "PENDING_APPROVAL",
    "message": "Request successfully ingested. High-value budget request routed to Notion for HOD approval.",
    "notion_url": "https://notion.so/workspace/REQ-20260819-A8F1"
  }
  ```

#### Endpoint 2: System Health Check
* **HTTP Method:** `GET /health`
* **Response Payload (HTTP 200 OK):**
  ```json
  {
    "status": "healthy",
    "engine": "campusdesk-backend",
    "notion_connected": true,
    "uptime_seconds": 3600
  }
  ```

---

## 2. Notion API Integration Protocol

CampusDesk AI interacts with Notion using the official REST API v2022-06-28 over HTTPS.

### 2.1 Notion Authorization
* Header: `Authorization: Bearer secret_xxxxxxxxxxxxxxxxxxxxxxxx`
* Header: `Notion-Version: 2022-06-28`

### 2.2 Schema Definitions for Notion Databases

#### Database A: `Student Requests` Database Schema
```json
{
  "parent": { "type": "page_id", "page_id": "<NOTION_PARENT_PAGE_ID>" },
  "title": [ { "type": "text", "text": { "content": "Student Requests" } } ],
  "properties": {
    "Request ID": { "title": {} },
    "Student Name": { "rich_text": {} },
    "Category": {
      "select": {
        "options": [
          { "name": "LEAVE", "color": "blue" },
          { "name": "BUDGET", "color": "green" },
          { "name": "LAB_EQUIPMENT", "color": "orange" },
          { "name": "GENERAL", "color": "gray" }
        ]
      }
    },
    "Status": {
      "select": {
        "options": [
          { "name": "Pending Approval", "color": "yellow" },
          { "name": "Auto-Approved", "color": "green" },
          { "name": "Approved", "color": "green" },
          { "name": "Rejected", "color": "red" }
        ]
      }
    },
    "Urgency": { "select": {} },
    "Amount (INR)": { "number": { "format": "rupee" } },
    "AI Reasoning Summary": { "rich_text": {} },
    "Created Time": { "created_time": {} }
  }
}
```

#### Database B: `System Run Log` Database Schema
```json
{
  "properties": {
    "Run ID": { "title": {} },
    "Request ID Ref": { "rich_text": {} },
    "Trigger Event": { "select": {} },
    "Action Executed": { "rich_text": {} },
    "Execution Time (ms)": { "number": {} },
    "Timestamp": { "date": {} },
    "Success": { "checkbox": {} }
  }
}
```

---

## 3. Asynchronous Human Approval Gate Poller

The background poller service (`src/notion/poller.py`) continuously checks for status changes made by human approvers inside Notion:

```python
async def poll_notion_approval_gate():
    """Polls Notion every 10 seconds for items moved to Approved/Rejected."""
    query_payload = {
        "filter": {
            "or": [
                {"property": "Status", "select": {"equals": "Approved"}},
                {"property": "Status", "select": {"equals": "Rejected"}}
            ]
        }
    }
    updated_pages = await notion_client.query_database(REQUESTS_DB_ID, query_payload)
    
    for page in updated_pages:
        # Check if action has already been executed for this page
        if not await is_action_already_executed(page['id']):
            await execute_approved_action(page)
            await mark_action_completed(page['id'])
```

---

## 4. Error Handling & Retry Policies
* **Notion API Rate Limits (HTTP 429):** Implements exponential backoff (`tenacity` library) with jitter: `wait_exponential(multiplier=1, min=2, max=10)`.
* **Transient Mail Dispatch Failures:** Retries email dispatch 3 times. If all retries fail, appends an error alert entry to the Notion Run Log and marks the request status as `FAILED_EMAIL_DISPATCH`.
