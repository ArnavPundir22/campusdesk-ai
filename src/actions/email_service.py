import logging
import base64
from typing import Optional
from src.config import settings
from src.models import StudentRequestDomainModel
from src.core.response_drafter import ResponseDrafterAgent
from src.actions.pdf_engine import PDFEngine

logger = logging.getLogger("campusdesk.email")


class EmailSender:
    """Service responsible for emailing decision notifications and attached PDF certificates."""

    @classmethod
    async def send_decision_email(
        cls,
        request: StudentRequestDomainModel,
        approver_notes: str = ""
    ) -> bool:
        draft = ResponseDrafterAgent.draft(request, approver_notes)
        pdf_bytes = PDFEngine.generate_approval_certificate(request)

        mock_mode = settings.MOCK_EMAIL or not settings.RESEND_API_KEY or settings.RESEND_API_KEY == "re_mock_key"

        if mock_mode:
            logger.info(
                f"[MOCK EMAIL DISPATCH] To: {request.contact_email} | Subject: '{draft.email_subject}' | "
                f"PDF Attached: {len(pdf_bytes)} bytes"
            )
            return True

        # Send via Resend API if key is available
        try:
            import resend
            resend.api_key = settings.RESEND_API_KEY

            pdf_b64 = base64.b64encode(pdf_bytes).decode("utf-8")
            params = {
                "from": settings.SENDER_EMAIL,
                "to": [request.contact_email],
                "subject": draft.email_subject,
                "html": draft.email_body_html,
                "attachments": [
                    {
                        "filename": f"Approval_Certificate_{request.request_id}.pdf",
                        "content": pdf_b64
                    }
                ]
            }
            resend.Emails.send(params)
            logger.info(f"Successfully dispatched email via Resend to {request.contact_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to dispatch email via Resend API: {e}")
            return False
