import httpx
import uuid
import logging
from typing import Dict, Any, List, Optional, Tuple
from src.config import settings
from src.models import StudentRequestDomainModel
from src.notion.formatter import NotionFormatter

logger = logging.getLogger("campusdesk.notion")


class NotionClient:
    """Asynchronous client for Notion REST API with Mock Mode fallback."""

    def __init__(self):
        self.api_key = settings.NOTION_API_KEY
        self.requests_db_id = settings.NOTION_REQUESTS_DB_ID
        self.run_log_db_id = settings.NOTION_RUN_LOG_DB_ID
        self.rulebook_db_id = settings.NOTION_RULEBOOK_DB_ID
        self.mock_mode = settings.MOCK_NOTION or not self.api_key or self.api_key == "secret_mock_token"

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }

        # Mock in-memory database store for testing
        self._mock_pages: Dict[str, Dict[str, Any]] = {}

    async def create_request_page(self, request: StudentRequestDomainModel) -> Tuple[str, str]:
        """Create a new page in the Student Requests database. Returns (page_id, page_url)."""
        if self.mock_mode:
            page_id = f"mock-page-{uuid.uuid4().hex[:8]}"
            page_url = f"https://notion.so/mockworkspace/{page_id}"
            
            # Store in mock store
            self._mock_pages[page_id] = {
                "id": page_id,
                "url": page_url,
                "request_id": request.request_id,
                "status": "Pending Approval" if request.status.value == "PENDING_APPROVAL" else "Auto-Approved",
                "request_domain": request,
                "action_executed": request.action_executed
            }
            logger.info(f"[MOCK NOTION] Created page {page_id} for request {request.request_id}")
            return page_id, page_url

        payload = NotionFormatter.build_page_payload(request, self.requests_db_id)
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post("https://api.notion.com/v1/pages", headers=self.headers, json=payload)
            response.raise_for_status()
            data = response.json()
            page_id = data.get("id", "")
            page_url = data.get("url", f"https://notion.so/{page_id.replace('-', '')}")
            return page_id, page_url

    async def query_pending_approvals(self) -> List[Dict[str, Any]]:
        """Query Notion for pages moved to 'Approved' or 'Rejected' by human approvers."""
        if self.mock_mode:
            results = []
            for p_id, p_data in self._mock_pages.items():
                if p_data.get("status") in ("Approved", "Rejected") and not p_data.get("action_executed"):
                    results.append({
                        "id": p_id,
                        "status": p_data.get("status"),
                        "request_id": p_data.get("request_id"),
                        "domain_model": p_data.get("request_domain")
                    })
            return results

        url = f"https://api.notion.com/v1/databases/{self.requests_db_id}/query"
        query_payload = {
            "filter": {
                "or": [
                    {"property": "Status", "select": {"equals": "Approved"}},
                    {"property": "Status", "select": {"equals": "Rejected"}}
                ]
            }
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, headers=self.headers, json=query_payload)
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])

    async def update_page_status(self, page_id: str, new_status: str) -> bool:
        """Update status property of a page in Notion database."""
        if self.mock_mode:
            if page_id in self._mock_pages:
                self._mock_pages[page_id]["status"] = new_status
                self._mock_pages[page_id]["action_executed"] = True
            return True

        url = f"https://api.notion.com/v1/pages/{page_id}"
        payload = {
            "properties": {
                "Status": {"select": {"name": new_status}}
            }
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.patch(url, headers=self.headers, json=payload)
                res.raise_for_status()
                logger.info(f"Updated Notion Page {page_id} Status -> '{new_status}'")
                return True
        except Exception as e:
            logger.error(f"Failed to update Notion page status for {page_id}: {e}")
            return False

    async def append_run_log(self, run_id: str, request_id: str, trigger_event: str, action_executed: str, execution_ms: int, success: bool = True) -> str:
        """Append timestamped row to System Run Log database."""
        if self.mock_mode:
            logger.info(f"[MOCK NOTION RUN LOG] {run_id} | Ref: {request_id} | Event: {trigger_event} | Action: {action_executed} ({execution_ms}ms)")
            return f"mock-log-{uuid.uuid4().hex[:8]}"

        payload = {
            "parent": {"database_id": self.run_log_db_id},
            "properties": {
                "Run ID": {"title": [{"type": "text", "text": {"content": run_id}}]},
                "Request ID Ref": {"rich_text": [{"type": "text", "text": {"content": request_id}}]},
                "Trigger Event": {"select": {"name": trigger_event}},
                "Action Executed": {"rich_text": [{"type": "text", "text": {"content": action_executed}}]},
                "Execution Time (ms)": {"number": execution_ms},
                "Success": {"checkbox": success}
            }
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post("https://api.notion.com/v1/pages", headers=self.headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("id", "")

    def simulate_human_approval(self, page_id: str, decision: str = "Approved"):
        """Simulate a human clicking 'Approved' or 'Rejected' inside Notion UI."""
        if page_id in self._mock_pages:
            self._mock_pages[page_id]["status"] = decision
            logger.info(f"[SIMULATION] Human updated Notion Page {page_id} Status -> '{decision}'")

    async def fetch_dynamic_rulebook(self) -> Dict[str, Dict[str, Any]]:
        """Fetch live rule configurations from Notion Rulebook Database with 60s TTL cache."""
        if self.mock_mode or not self.rulebook_db_id:
            return {}

        now = time.time()
        if hasattr(self, "_rulebook_cache") and hasattr(self, "_rulebook_cache_time"):
            if now - self._rulebook_cache_time < 60.0:
                return self._rulebook_cache

        url = f"https://api.notion.com/v1/databases/{self.rulebook_db_id}/query"
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.post(url, headers=self.headers, json={})
                if res.status_code == 200:
                    rules_map = {}
                    for row in res.json().get("results", []):
                        props = row.get("properties", {})
                        r_id_list = props.get("Rule ID", {}).get("title", [])
                        if not r_id_list:
                            continue
                        r_id = r_id_list[0].get("text", {}).get("content", "")
                        auto_approve = props.get("Auto Approve Enabled", {}).get("checkbox", False)
                        max_budget = props.get("Max Auto Budget (INR)", {}).get("number") or 0.0
                        max_leave = props.get("Max Auto Leave Days", {}).get("number") or 0
                        rules_map[r_id] = {
                            "auto_approve": auto_approve,
                            "max_budget": max_budget,
                            "max_leave": max_leave
                        }
                    self._rulebook_cache = rules_map
                    self._rulebook_cache_time = now
                    return rules_map
        except Exception as e:
            logger.warning(f"Could not fetch dynamic rulebook from Notion: {e}")
        return getattr(self, "_rulebook_cache", {})


notion_client = NotionClient()

