import httpx
import asyncio
import os
import sys
from src.config import settings


async def create_rulebook_database(parent_page_id: str):
    """Programmatically create Rulebook Database inside parent Notion page and seed default rules."""
    api_key = settings.NOTION_API_KEY
    if not api_key or api_key == "secret_mock_token":
        print("❌ Error: NOTION_API_KEY is not configured in .env file.")
        return

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    clean_parent_id = parent_page_id.split("/")[-1].split("?")[0].replace("-", "")

    async with httpx.AsyncClient(timeout=15.0) as client:
        print("⚙️ Creating 'Rulebook Database' in Notion Control Center...")
        db_payload = {
            "parent": {"type": "page_id", "page_id": clean_parent_id},
            "title": [{"type": "text", "text": {"content": "CampusDesk Rulebook"}}],
            "properties": {
                "Rule ID": {"title": {}},
                "Category": {
                    "select": {
                        "options": [
                            {"name": "BUDGET", "color": "green"},
                            {"name": "LEAVE", "color": "blue"},
                            {"name": "LAB_EQUIPMENT", "color": "orange"},
                            {"name": "EVENT_HALL", "color": "purple"},
                            {"name": "GENERAL", "color": "gray"},
                            {"name": "ALL", "color": "red"}
                        ]
                    }
                },
                "Auto Approve Enabled": {"checkbox": {}},
                "Max Auto Budget (INR)": {"number": {"format": "number"}},
                "Max Auto Leave Days": {"number": {"format": "number"}},
                "Rule Description": {"rich_text": {}}
            }
        }

        res = await client.post("https://api.notion.com/v1/databases", headers=headers, json=db_payload)
        if res.status_code != 200:
            print(f"❌ Failed to create Rulebook database: {res.status_code} - {res.text}")
            return

        db_data = res.json()
        rulebook_db_id = db_data["id"]
        print(f"✅ Created Rulebook Database ID: {rulebook_db_id}")

        # Seed 6 Default Rules
        print("⚙️ Seeding 6 Default Managing Rules into Notion Rulebook...")
        default_rules = [
            {
                "id": "R1_GLOBAL_DRAFT",
                "cat": "ALL",
                "auto": False,
                "max_budget": 0,
                "max_leave": 0,
                "desc": "Draft/Unparsed status fallback requires human review."
            },
            {
                "id": "R2_BUDGET_THRESHOLD",
                "cat": "BUDGET",
                "auto": True,
                "max_budget": 1000.0,
                "max_leave": 0,
                "desc": "Budget requests under Max Auto Budget (default ₹1,000) are auto-approved. Higher amounts pause at Notion Human Gate."
            },
            {
                "id": "R3_LEAVE_THRESHOLD",
                "cat": "LEAVE",
                "auto": True,
                "max_budget": 0,
                "max_leave": 1,
                "desc": "Leave requests up to Max Auto Leave Days (default 1 day) are auto-approved. Multi-day leaves require approval."
            },
            {
                "id": "R4_RESOURCE_GATE",
                "cat": "LAB_EQUIPMENT",
                "auto": False,
                "max_budget": 0,
                "max_leave": 0,
                "desc": "Physical lab equipment and HPC borrowing always requires lab coordinator verification in Notion."
            },
            {
                "id": "R5_EVENT_GATE",
                "cat": "EVENT_HALL",
                "auto": False,
                "max_budget": 0,
                "max_leave": 0,
                "desc": "Auditorium and seminar hall bookings require venue manager verification."
            },
            {
                "id": "R6_GENERAL_GATE",
                "cat": "GENERAL",
                "auto": False,
                "max_budget": 0,
                "max_leave": 0,
                "desc": "Uncategorized general academic requests pause for administrative routing."
            }
        ]

        for rule in default_rules:
            row_payload = {
                "parent": {"database_id": rulebook_db_id},
                "properties": {
                    "Rule ID": {"title": [{"type": "text", "text": {"content": rule["id"]}}]},
                    "Category": {"select": {"name": rule["cat"]}},
                    "Auto Approve Enabled": {"checkbox": rule["auto"]},
                    "Max Auto Budget (INR)": {"number": rule["max_budget"]},
                    "Max Auto Leave Days": {"number": rule["max_leave"]},
                    "Rule Description": {"rich_text": [{"type": "text", "text": {"content": rule["desc"]}}]}
                }
            }
            await client.post("https://api.notion.com/v1/pages", headers=headers, json=row_payload)

        print("\n🎉 RULEBOOK SETUP COMPLETE!")
        print(f"Rulebook Database ID: {rulebook_db_id}")
        print("\nAdd this line to your .env file:")
        print(f"NOTION_RULEBOOK_DB_ID={rulebook_db_id}")


if __name__ == "__main__":
    parent_id = sys.argv[1] if len(sys.argv) > 1 else "3c282ead-0f2a-80de-8525-dbde33eacc9b"
    asyncio.run(create_rulebook_database(parent_id))
