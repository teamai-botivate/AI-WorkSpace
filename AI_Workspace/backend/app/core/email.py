"""
Shared Email Service

Unified async SMTP sender used by all agents.
Supports HTML templates via Jinja2.
"""

import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import aiosmtplib

from ..config import get_settings

logger = logging.getLogger("botivate.core.email")


class EmailService:
    """Async email sender using SMTP."""

    def __init__(self):
        self.settings = get_settings()

    async def send_email(
        self,
        to: str | list[str],
        subject: str,
        body_html: str,
        body_text: str | None = None,
        from_name: str | None = None,
    ) -> bool:
        """
        Send an email via SMTP.

        Args:
            to: Recipient email(s)
            subject: Email subject
            body_html: HTML body content
            body_text: Optional plain text fallback
            from_name: Sender display name (defaults to app name)

        Returns:
            True if sent successfully, False otherwise.
        """
        if not self.settings.smtp_user or not self.settings.smtp_password:
            logger.warning("SMTP credentials not configured — email not sent")
            return False

        sender_name = from_name or self.settings.app_name
        sender_email = self.settings.smtp_user
        recipients = [to] if isinstance(to, str) else to

        msg = MIMEMultipart("alternative")
        msg["From"] = f"{sender_name} <{sender_email}>"
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = subject

        if body_text:
            msg.attach(MIMEText(body_text, "plain"))
        msg.attach(MIMEText(body_html, "html"))

        try:
            await aiosmtplib.send(
                msg,
                hostname=self.settings.smtp_server,
                port=self.settings.smtp_port,
                username=self.settings.smtp_user,
                password=self.settings.smtp_password,
                start_tls=True,
            )
            logger.info(f"Email sent to {', '.join(recipients)}: {subject}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {', '.join(recipients)}: {e}")
            return False

    async def send_template_email(
        self,
        to: str | list[str],
        subject: str,
        template_html: str,
        context: dict | None = None,
    ) -> bool:
        """Send an email using a Jinja2 HTML template string."""
        from jinja2 import Template

        ctx = context or {}
        ctx.setdefault("app_name", self.settings.app_name)
        ctx.setdefault("app_url", self.settings.app_url)

        template = Template(template_html)
        rendered = template.render(**ctx)
        return await self.send_email(to=to, subject=subject, body_html=rendered)
