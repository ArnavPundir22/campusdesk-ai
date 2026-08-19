import pytest
from src.notion.client import notion_client
from src.notion.poller import notion_poller
from src.models import WorkflowStatus


@pytest.mark.asyncio
async def test_health_check_endpoint(async_client):
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["engine"] == "campusdesk-backend"


@pytest.mark.asyncio
async def test_auto_approval_ingestion_flow(async_client):
    payload = {
        "student_name": "Aarav Sharma",
        "student_id": "2023-CS-042",
        "contact_email": "aarav.sharma@university.edu.in",
        "raw_text": "Sir, requesting reimbursement of Rs 850 for purchasing lab wires.",
        "department": "Computer Science"
    }

    response = await async_client.post("/api/v1/requests/submit", json=payload)
    assert response.status_code == 201
    data = response.json()

    assert data["status"] == "success"
    assert data["duplicate_detected"] is False
    assert data["workflow_status"] == "AUTO_APPROVED"
    assert "REQ-" in data["request_id"]
    assert "notion_url" in data


@pytest.mark.asyncio
async def test_human_gated_ingestion_and_polling_flow(async_client):
    payload = {
        "student_name": "Priya Verma",
        "student_id": "2023-ECE-108",
        "contact_email": "priya.verma@university.edu.in",
        "raw_text": "Requesting budget reimbursement of Rs 4,500 spent on high-precision oscilloscope sensors for final year project.",
        "department": "Electronics"
    }

    # Step 1: Ingest request -> Should pause at PENDING_APPROVAL gate
    response = await async_client.post("/api/v1/requests/submit", json=payload)
    assert response.status_code == 201
    data = response.json()

    assert data["workflow_status"] == "PENDING_APPROVAL"
    req_id = data["request_id"]

    # Retrieve created mock page ID
    mock_pages = notion_client._mock_pages
    matching_page_id = None
    for p_id, p_info in mock_pages.items():
        if p_info.get("request_id") == req_id:
            matching_page_id = p_id
            break

    assert matching_page_id is not None, "Mock Notion page was not created"

    # Step 2: Simulate Human Approver clicking 'Approved' in Notion
    notion_client.simulate_human_approval(matching_page_id, decision="Approved")

    # Step 3: Trigger poller iteration
    await notion_poller.check_approval_gate_transitions()

    # Step 4: Verify action was executed
    assert mock_pages[matching_page_id]["request_domain"].action_executed is True
    assert mock_pages[matching_page_id]["request_domain"].status == WorkflowStatus.APPROVED


@pytest.mark.asyncio
async def test_idempotency_deduplication(async_client):
    payload = {
        "student_name": "Aarav Sharma",
        "student_id": "2023-CS-042",
        "contact_email": "aarav.sharma@university.edu.in",
        "raw_text": "Sir, emergency leave required for 1 day due to medical checkup.",
        "department": "Computer Science"
    }

    # First submission
    res1 = await async_client.post("/api/v1/requests/submit", json=payload)
    assert res1.status_code == 201
    d1 = res1.json()
    assert d1["duplicate_detected"] is False

    # Immediate duplicate submission
    res2 = await async_client.post("/api/v1/requests/submit", json=payload)
    assert res2.status_code == 201
    d2 = res2.json()

    assert d2["duplicate_detected"] is True
    assert d2["request_id"] == d1["request_id"]
