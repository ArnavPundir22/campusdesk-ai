import os
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

        # 1. Always Save PDF Certificate locally in pdf_certificates/ for easy user access
        pdf_dir = os.path.join(os.getcwd(), "pdf_certificates")
        os.makedirs(pdf_dir, exist_ok=True)
        pdf_filepath = os.path.join(pdf_dir, f"Approval_Certificate_{request.request_id}.pdf")
        with open(pdf_filepath, "wb") as f:
            f.write(pdf_bytes)
        logger.info(f"📄 Saved PDF Approval Certificate locally: {pdf_filepath}")

        mock_mode = settings.MOCK_EMAIL or not settings.RESEND_API_KEY or settings.RESEND_API_KEY == "re_mock_key"

        if mock_mode:
            logger.info(
                f"[MOCK EMAIL DISPATCH] To: {request.contact_email} | Subject: '{draft.email_subject}' | "
                f"PDF Saved: {pdf_filepath}"
            )
            return True

        # 2. Send via Resend API
        try:
            import resend
            resend.api_key = settings.RESEND_API_KEY

            pdf_b64 = base64.b64encode(pdf_bytes).decode("utf-8")
            
            # Primary recipient or fallback to Resend registered account
            recipient = request.contact_email or "abhivanshrana22@gmail.com"
            
            params = {
                "from": settings.SENDER_EMAIL,
                "to": [recipient],
                "subject": draft.email_subject,
                "html": draft.email_body_html,
                "attachments": [
                    {
                        "filename": f"Approval_Certificate_{request.request_id}.pdf",
                        "content": pdf_b64
                    }
                ]
            }
            
            try:
                resend.Emails.send(params)
                logger.info(f"Successfully dispatched email via Resend to {recipient}")
                return True
            except Exception as send_err:
                err_msg = str(send_err)
                if "only send testing emails to your own email address" in err_msg:
                    logger.warning(f"Resend test mode restricted delivery. Falling back to account owner email (abhivanshrana22@gmail.com).")
                    params["to"] = ["abhivanshrana22@gmail.com"]
                    resend.Emails.send(params)
                    logger.info("Successfully dispatched fallback email to Resend owner email (abhivanshrana22@gmail.com).")
                    return True
                raise send_err

        except Exception as e:
            logger.error(f"Failed to dispatch email via Resend API: {e}")
            return False
