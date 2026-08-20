import httpx
import asyncio
import sys
import os
from src.config import settings
from src.notion.client import notion_client


async def create_notion_databases(parent_page_id: str):
    """Programmatically create Student Requests and System Run Log databases inside a parent Notion page."""
    api_key = settings.NOTION_API_KEY
    if not api_key or api_key == "secret_mock_token":
        print("❌ Error: NOTION_API_KEY is not set in .env file.")
        return

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    # Clean parent_page_id (remove hyphens if formatted as URL or raw UUID)
    clean_parent_id = parent_page_id.split("/")[-1].split("?")[0].replace("-", "")

    async with httpx.AsyncClient(timeout=15.0) as client:
        # 1. Create Student Requests Database
        print("⚙️ Creating 'Student Requests' Database in Notion...")
        db1_payload = {
            "parent": {"type": "page_id", "page_id": clean_parent_id},
            "title": [{"type": "text", "text": {"content": "Student Requests"}}],
            "properties": {
                "Request ID": {"title": {}},
                "Student Name": {"rich_text": {}},
                "Category": {
                    "select": {
                        "options": [
                            {"name": "LEAVE", "color": "blue"},
                            {"name": "BUDGET", "color": "green"},
                            {"name": "LAB_EQUIPMENT", "color": "orange"},
                            {"name": "EVENT_HALL", "color": "purple"},
                            {"name": "GENERAL", "color": "gray"}
                        ]
                    }
                },
                "Status": {
                    "select": {
                        "options": [
                            {"name": "Pending Approval", "color": "yellow"},
                            {"name": "Auto-Approved", "color": "green"},
                            {"name": "Approved", "color": "green"},
                            {"name": "Rejected", "color": "red"}
                        ]
                    }
                },
                "Urgency": {
                    "select": {
                        "options": [
                            {"name": "LOW", "color": "blue"},
                            {"name": "MEDIUM", "color": "yellow"},
                            {"name": "HIGH", "color": "orange"},
                            {"name": "CRITICAL", "color": "red"}
                        ]
                    }
                },
                "Amount (INR)": {"number": {"format": "number"}},
                "AI Reasoning Summary": {"rich_text": {}}
            }
        }

        resp1 = await client.post("https://api.notion.com/v1/databases", headers=headers, json=db1_payload)
        if resp1.status_code != 200:
            print(f"❌ Failed to create Student Requests Database: {resp1.status_code} - {resp1.text}")
            return
        
        db1_data = resp1.json()
        db1_id = db1_data["id"]
        print(f"✅ 'Student Requests' Database created! ID: {db1_id}")

        # 2. Create System Run Log Database
        print("⚙️ Creating 'System Run Log' Database in Notion...")
        db2_payload = {
            "parent": {"type": "page_id", "page_id": clean_parent_id},
            "title": [{"type": "text", "text": {"content": "System Run Log"}}],
            "properties": {
                "Run ID": {"title": {}},
                "Request ID Ref": {"rich_text": {}},
                "Trigger Event": {
                    "select": {
                        "options": [
                            {"name": "WEBHOOK_INGESTION", "color": "blue"},
                            {"name": "HUMAN_APPROVAL_GATE", "color": "green"}
                        ]
                    }
                },
                "Action Executed": {"rich_text": {}},
                "Execution Time (ms)": {"number": {"format": "number"}},
                "Success": {"checkbox": {}}
            }
        }

        resp2 = await client.post("https://api.notion.com/v1/databases", headers=headers, json=db2_payload)
        if resp2.status_code != 200:
            print(f"❌ Failed to create System Run Log Database: {resp2.status_code} - {resp2.text}")
            return

        db2_data = resp2.json()
        db2_id = db2_data["id"]
        print(f"✅ 'System Run Log' Database created! ID: {db2_id}")

        # Print env updates
        print("\n🎉 AUTOMATIC SETUP COMPLETE!")
        print("Update your .env file with these Database IDs:")
        print(f"NOTION_REQUESTS_DB_ID={db1_id}")
        print(f"NOTION_RUN_LOG_DB_ID={db2_id}")
        print("MOCK_NOTION=false")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m src.notion.setup_workspace <PARENT_PAGE_ID_OR_URL>")
        sys.exit(1)
    asyncio.run(create_notion_databases(sys.argv[1]))
