from typing import List, Dict, Any
from src.models import StudentRequestDomainModel, WorkflowStatus, RequestCategory


class NotionFormatter:
    """Builds clean, human-readable Notion page blocks avoiding raw JSON dumps."""

    @staticmethod
    def get_category_emoji(category: RequestCategory) -> str:
        mapping = {
            RequestCategory.LEAVE: "📝",
            RequestCategory.BUDGET: "💰",
            RequestCategory.LAB_EQUIPMENT: "🔬",
            RequestCategory.EVENT_HALL: "🎪",
            RequestCategory.GENERAL: "📄"
        }
        return mapping.get(category, "📄")

    @staticmethod
    def get_status_color(status: WorkflowStatus) -> str:
        mapping = {
            WorkflowStatus.AUTO_APPROVED: "green",
            WorkflowStatus.APPROVED: "green",
            WorkflowStatus.PENDING_APPROVAL: "yellow",
            WorkflowStatus.REJECTED: "red",
            WorkflowStatus.FAILED: "red"
        }
        return mapping.get(status, "gray")

    @classmethod
    def build_page_payload(cls, request: StudentRequestDomainModel, database_id: str) -> Dict[str, Any]:
        """Construct database page creation API payload with styled properties and rich blocks."""
        emoji = cls.get_category_emoji(request.category)
        
        status_map = {
            WorkflowStatus.AUTO_APPROVED: "Auto-Approved",
            WorkflowStatus.APPROVED: "Approved",
            WorkflowStatus.PENDING_APPROVAL: "Pending Approval",
            WorkflowStatus.REJECTED: "Rejected",
            WorkflowStatus.FAILED: "Failed"
        }
        status_name = status_map.get(request.status, "Pending Approval")

        properties = {
            "Request ID": {
                "title": [{"type": "text", "text": {"content": request.request_id}}]
            },
            "Student Name": {
                "rich_text": [{"type": "text", "text": {"content": f"{request.student_name} ({request.student_id or 'N/A'})"}}]
            },
            "Category": {
                "select": {"name": request.category.value}
            },
            "Status": {
                "select": {"name": status_name}
            },
            "Urgency": {
                "select": {"name": request.urgency.value}
            },
            "Amount (INR)": {
                "number": request.amount_inr
            },
            "AI Reasoning Summary": {
                "rich_text": [{"type": "text", "text": {"content": request.summary[:2000]}}]
            }
        }

        # Page body blocks layout
        children_blocks = [
            # Block 1: Executive Summary Callout
            {
                "object": "block",
                "type": "callout",
                "callout": {
                    "icon": {"type": "emoji", "emoji": "💡"},
                    "color": "gray_background",
                    "rich_text": [
                        {"type": "text", "text": {"content": "EXECUTIVE SUMMARY\n", "annotations": {"bold": True}}},
                        {"type": "text", "text": {"content": request.summary}}
                    ]
                }
            },
            # Block 2: System Assessment Toggle List
            {
                "object": "block",
                "type": "toggle",
                "toggle": {
                    "rich_text": [{"type": "text", "text": {"content": "⚙️ System Logic & Rule Evaluation", "annotations": {"bold": True}}}],
                    "children": [
                        {
                            "object": "block",
                            "type": "bulleted_list_item",
                            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": f"Rule Evaluated: {request.decision_reason}"}}]}
                        },
                        {
                            "object": "block",
                            "type": "bulleted_list_item",
                            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": f"Category Assigned: {request.category.value}"}}]}
                        },
                        {
                            "object": "block",
                            "type": "bulleted_list_item",
                            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": f"Idempotency Hash: {request.idempotency_hash[:16]}..."}}]}
                        }
                    ]
                }
            }
        ]

        # Block 3: Human Approver Action Board Callout if Pending Approval
        if request.status == WorkflowStatus.PENDING_APPROVAL:
            children_blocks.append({
                "object": "block",
                "type": "callout",
                "callout": {
                    "icon": {"type": "emoji", "emoji": "🙋"},
                    "color": "yellow_background",
                    "rich_text": [
                        {"type": "text", "text": {"content": "ACTION REQUIRED BY APPROVER\n", "annotations": {"bold": True}}},
                        {"type": "text", "text": {"content": "Please review the request details and change the 'Status' property above to 'Approved' or 'Rejected' to execute downstream real-world actions."}}
                    ]
                }
            })

        # Block 4: Original Text Submission Quote
        children_blocks.append({
            "object": "block",
            "type": "quote",
            "quote": {
                "rich_text": [
                    {"type": "text", "text": {"content": "Original Student Submission:\n", "annotations": {"italic": True}}},
                    {"type": "text", "text": {"content": request.raw_text}}
                ]
            }
        })

        return {
            "parent": {"database_id": database_id},
            "icon": {"type": "emoji", "emoji": emoji},
            "properties": properties,
            "children": children_blocks
        }
