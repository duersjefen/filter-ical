"""
Email notification service for domain requests.

IMPERATIVE SHELL - Handles email sending with SMTP.
"""

import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Tuple
import logging

from ..core.config import settings
from ..models.domain_request import DomainRequest

logger = logging.getLogger(__name__)


async def send_domain_request_notification(request: DomainRequest) -> Tuple[bool, str]:
    """
    Send email notification to admin when new domain request is submitted.

    Args:
        request: DomainRequest object

    Returns:
        Tuple of (success, error_message)
    """
    # Skip if email not configured
    if not settings.admin_email or not settings.smtp_username:
        logger.warning("Email not configured - skipping notification")
        return True, ""  # Don't fail the request

    try:
        # Create email message
        message = MIMEMultipart("alternative")
        message["Subject"] = f"🎯 New Custom Domain Request from {request.username}"
        message["From"] = settings.smtp_from_email
        message["To"] = settings.admin_email

        # Create HTML email body
        html_body = f"""
        <html>
          <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 20px;">
              <h1 style="margin: 0; font-size: 24px;">🎯 New Custom Domain Request</h1>
            </div>

            <div style="background: #f7fafc; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
              <h2 style="color: #2d3748; margin-top: 0;">Request Details</h2>

              <div style="margin-bottom: 15px;">
                <strong style="color: #4a5568;">Username:</strong><br/>
                <span style="color: #2d3748;">{request.username}</span>
              </div>

              <div style="margin-bottom: 15px;">
                <strong style="color: #4a5568;">Calendar URL:</strong><br/>
                <a href="{request.calendar_url}" style="color: #667eea; word-break: break-all;">{request.calendar_url}</a>
              </div>

              <div style="margin-bottom: 15px;">
                <strong style="color: #4a5568;">Description:</strong><br/>
                <p style="color: #2d3748; margin: 5px 0; padding: 10px; background: white; border-radius: 5px;">
                  {request.description}
                </p>
              </div>

              <div style="margin-bottom: 15px;">
                <strong style="color: #4a5568;">Request ID:</strong><br/>
                <span style="color: #2d3748;">#{request.id}</span>
              </div>

              <div>
                <strong style="color: #4a5568;">Submitted:</strong><br/>
                <span style="color: #2d3748;">{request.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")}</span>
              </div>
            </div>

            <div style="background: #edf2f7; padding: 20px; border-radius: 10px;">
              <h3 style="color: #2d3748; margin-top: 0;">Next Steps</h3>
              <p style="color: #4a5568; margin: 10px 0;">
                1. Log in to the admin panel at <a href="https://filter-ical.de/admin" style="color: #667eea;">filter-ical.de/admin</a><br/>
                2. Review the request details and calendar URL<br/>
                3. Approve or reject the request
              </p>
            </div>

            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e2e8f0; text-align: center; color: #a0aec0; font-size: 12px;">
              <p>This is an automated notification from Filter iCal</p>
            </div>
          </body>
        </html>
        """

        # Create plain text version as fallback
        text_body = f"""
New Custom Domain Request

Username: {request.username}
Calendar URL: {request.calendar_url}
Description: {request.description}
Request ID: #{request.id}
Submitted: {request.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")}

Next Steps:
1. Log in to the admin panel at https://filter-ical.de/admin
2. Review the request details
3. Approve or reject the request

---
This is an automated notification from Filter iCal
        """

        # Attach both versions
        part1 = MIMEText(text_body, "plain")
        part2 = MIMEText(html_body, "html")
        message.attach(part1)
        message.attach(part2)

        # Send email
        await aiosmtplib.send(
            message,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_username,
            password=settings.smtp_password,
            start_tls=True,
        )

        logger.info(f"Domain request notification sent to {settings.admin_email}")
        return True, ""

    except Exception as e:
        error_msg = f"Failed to send email notification: {str(e)}"
        logger.error(error_msg)
        return False, error_msg
