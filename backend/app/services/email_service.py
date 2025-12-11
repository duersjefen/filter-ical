"""
Email notification service using AWS SES.

IMPERATIVE SHELL - Handles email sending with AWS SES.
"""

import asyncio
import logging
from typing import Tuple

import boto3
from botocore.exceptions import ClientError

from ..core.config import settings
from ..models.domain_request import DomainRequest

logger = logging.getLogger(__name__)

# Initialize SES client (lazy - created on first use)
_ses_client = None


def _get_ses_client():
    """Get or create SES client."""
    global _ses_client
    if _ses_client is None:
        _ses_client = boto3.client('ses', region_name=settings.ses_region)
    return _ses_client


def _send_email_sync(to_email: str, subject: str, html_body: str, text_body: str, reply_to: str = None) -> Tuple[bool, str]:
    """Synchronous helper to send email via SES."""
    try:
        ses = _get_ses_client()

        email_params = {
            'Source': settings.ses_from_email,
            'Destination': {'ToAddresses': [to_email]},
            'Message': {
                'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                'Body': {
                    'Text': {'Data': text_body, 'Charset': 'UTF-8'},
                    'Html': {'Data': html_body, 'Charset': 'UTF-8'}
                }
            }
        }

        if reply_to:
            email_params['ReplyToAddresses'] = [reply_to]

        response = ses.send_email(**email_params)
        message_id = response.get('MessageId', 'unknown')
        logger.info(f"Email sent to {to_email} (MessageId: {message_id})")
        return True, ""

    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        error_msg = e.response.get('Error', {}).get('Message', str(e))
        logger.error(f"SES error ({error_code}): {error_msg}")
        return False, f"{error_code}: {error_msg}"
    except Exception as e:
        error_msg = f"Failed to send email: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


async def _send_email(to_email: str, subject: str, html_body: str, text_body: str, reply_to: str = None) -> Tuple[bool, str]:
    """Async wrapper for sending emails via SES."""
    return await asyncio.to_thread(_send_email_sync, to_email, subject, html_body, text_body, reply_to)


async def send_domain_request_notification(request: DomainRequest) -> Tuple[bool, str]:
    """
    Send email notification to admin when new domain request is submitted.

    Args:
        request: DomainRequest object

    Returns:
        Tuple of (success, error_message)
    """
    if not settings.admin_email:
        logger.warning("Admin email not configured - skipping notification")
        return True, ""

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

    return await _send_email(
        settings.admin_email,
        f"🎯 New Custom Domain Request from {request.username}",
        html_body,
        text_body
    )


async def send_password_reset_email(user_email: str, username: str, reset_token: str) -> Tuple[bool, str]:
    """
    Send password reset email to user.

    Args:
        user_email: User's email address
        username: User's username
        reset_token: Password reset token

    Returns:
        Tuple of (success, error_message)
    """
    logger.info(f"📧 Attempting to send password reset email to {user_email}")

    # Create reset URL based on environment
    if settings.is_development:
        base_url = "http://localhost:8000"
    elif settings.is_staging:
        base_url = "https://staging.filter-ical.de"
    else:
        base_url = "https://filter-ical.de"
    reset_url = f"{base_url}/reset-password?token={reset_token}"

    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 20px;">
          <h1 style="margin: 0; font-size: 24px;">🔐 Password Reset Request</h1>
        </div>

        <div style="background: #f7fafc; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
          <p style="color: #2d3748; margin-top: 0;">Hi <strong>{username}</strong>,</p>

          <p style="color: #2d3748;">
            We received a request to reset your password for your Filter iCal account.
          </p>

          <p style="color: #2d3748;">
            Click the button below to reset your password:
          </p>

          <div style="text-align: center; margin: 30px 0;">
            <a href="{reset_url}" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">
              Reset Password
            </a>
          </div>

          <p style="color: #718096; font-size: 12px;">
            Or copy and paste this link into your browser:<br/>
            <a href="{reset_url}" style="color: #667eea; word-break: break-all;">{reset_url}</a>
          </p>
        </div>

        <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
          <p style="color: #856404; margin: 0; font-size: 14px;">
            <strong>⚠️ Important:</strong> This link expires in 1 hour for security reasons.
          </p>
        </div>

        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
          <p style="color: #6c757d; margin: 0; font-size: 13px;">
            If you didn't request this password reset, you can safely ignore this email.
            Your password will remain unchanged.
          </p>
        </div>

        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e2e8f0; text-align: center; color: #a0aec0; font-size: 12px;">
          <p>This is an automated email from Filter iCal</p>
          <p style="margin-top: 10px;">
            <a href="https://filter-ical.de" style="color: #667eea; text-decoration: none;">filter-ical.de</a>
          </p>
        </div>
      </body>
    </html>
    """

    text_body = f"""
Password Reset Request - Filter iCal

Hi {username},

We received a request to reset your password for your Filter iCal account.

To reset your password, click the following link:
{reset_url}

This link expires in 1 hour for security reasons.

If you didn't request this password reset, you can safely ignore this email.
Your password will remain unchanged.

---
This is an automated email from Filter iCal
https://filter-ical.de
    """

    return await _send_email(
        user_email,
        "🔐 Password Reset Request - Filter iCal",
        html_body,
        text_body
    )


async def send_domain_approval_email(request: DomainRequest, domain_key: str, custom_message: str = None) -> Tuple[bool, str]:
    """Send approval email to user."""
    domain_url = f"https://filter-ical.de/{domain_key}"

    custom_msg_html = ""
    custom_msg_text = ""
    if custom_message:
        custom_msg_html = f"""
        <div style="background: #eff6ff; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #3b82f6;">
          <p style="margin: 0; color: #1e40af;"><strong>Message from admin:</strong></p>
          <p style="margin: 10px 0 0 0; color: #1e3a8a;">{custom_message}</p>
        </div>
        """
        custom_msg_text = f"\n\nMessage from admin:\n{custom_message}\n"

    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 20px;">
          <h1 style="margin: 0; font-size: 24px;">✅ Domain Approved!</h1>
        </div>
        <p>Hi <strong>{request.username}</strong>,</p>
        <p>Your domain <strong>{domain_key}</strong> is now live!</p>
        {custom_msg_html}
        <p>📍 <a href="{domain_url}">{domain_url}</a></p>
        <p>🔧 <a href="{domain_url}/admin">Manage your calendar</a></p>
      </body>
    </html>
    """

    text_body = f"""
Hi {request.username},

Your domain {domain_key} is now live!
{custom_msg_text}
📍 {domain_url}
🔧 {domain_url}/admin
    """

    return await _send_email(
        request.email,
        "✅ Your Custom Domain is Live!",
        html_body,
        text_body
    )


async def send_domain_rejection_email(request: DomainRequest, reason: str) -> Tuple[bool, str]:
    """Send rejection email to user."""
    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 20px;">
          <h1 style="margin: 0; font-size: 24px;">Domain Request Update</h1>
        </div>
        <p>Hi <strong>{request.username}</strong>,</p>
        <p>We're unable to approve your domain request at this time.</p>
        <p><strong>Reason:</strong><br/>{reason}</p>
        <p>Feel free to submit a new request after addressing these concerns.</p>
      </body>
    </html>
    """

    text_body = f"""
Hi {request.username},

We're unable to approve your domain request at this time.

Reason:
{reason}

Feel free to submit a new request after addressing these concerns.
    """

    return await _send_email(
        request.email,
        "Domain Request Update",
        html_body,
        text_body
    )


async def send_admin_password_reset_email(email: str, reset_token: str) -> Tuple[bool, str]:
    """
    Send admin password reset email.

    Args:
        email: Admin email address
        reset_token: Password reset token

    Returns:
        Tuple of (success, error_message)
    """
    logger.info(f"📧 Attempting to send admin password reset email to {email}")

    # Create reset URL based on environment
    if settings.is_development:
        base_url = "http://localhost:8000"
    elif settings.is_staging:
        base_url = "https://staging.filter-ical.de"
    else:
        base_url = "https://filter-ical.de"
    reset_url = f"{base_url}/admin/reset-password?token={reset_token}"

    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #9333ea 0%, #7e22ce 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 20px;">
          <h1 style="margin: 0; font-size: 24px;">🔐 Admin Password Reset</h1>
        </div>

        <div style="background: #f7fafc; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
          <p style="color: #2d3748; margin-top: 0;">Hi <strong>Admin</strong>,</p>

          <p style="color: #2d3748;">
            A password reset was requested for the Filter iCal admin panel.
          </p>

          <p style="color: #2d3748;">
            Click the button below to reset your admin password:
          </p>

          <div style="text-align: center; margin: 30px 0;">
            <a href="{reset_url}" style="background: linear-gradient(135deg, #9333ea 0%, #7e22ce 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">
              Reset Admin Password
            </a>
          </div>

          <p style="color: #718096; font-size: 12px;">
            Or copy and paste this link into your browser:<br/>
            <a href="{reset_url}" style="color: #9333ea; word-break: break-all;">{reset_url}</a>
          </p>
        </div>

        <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
          <p style="color: #856404; margin: 0; font-size: 14px;">
            <strong>⚠️ Important:</strong> This link expires in 1 hour for security reasons.
          </p>
        </div>

        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
          <p style="color: #6c757d; margin: 0; font-size: 13px;">
            If you didn't request this password reset, please ignore this email.
            Your password will remain unchanged.
          </p>
        </div>

        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e2e8f0; text-align: center; color: #a0aec0; font-size: 12px;">
          <p>This is an automated email from Filter iCal Admin</p>
          <p style="margin-top: 10px;">
            <a href="https://filter-ical.de/admin" style="color: #9333ea; text-decoration: none;">filter-ical.de/admin</a>
          </p>
        </div>
      </body>
    </html>
    """

    text_body = f"""
Admin Password Reset - Filter iCal

A password reset was requested for the Filter iCal admin panel.

Reset your password by visiting this link:
{reset_url}

⚠️ IMPORTANT: This link expires in 1 hour for security reasons.

If you didn't request this password reset, you can safely ignore this email.

---
This is an automated email from Filter iCal Admin
filter-ical.de/admin
    """

    return await _send_email(
        email,
        "🔐 Admin Password Reset - Filter iCal",
        html_body,
        text_body
    )


async def send_contact_form_email(name: str, email: str, subject: str, message: str) -> Tuple[bool, str]:
    """
    Send contact form submission to admin.

    Args:
        name: Sender's name
        email: Sender's email
        subject: Message subject
        message: Message content

    Returns:
        Tuple of (success, error_message)
    """
    if not settings.admin_email:
        logger.warning("Admin email not configured - skipping contact form notification")
        return False, "Email not configured"

    logger.info(f"📧 Sending contact form email from {email}")

    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 20px;">
          <h1 style="margin: 0; font-size: 24px;">💬 New Contact Form Message</h1>
        </div>

        <div style="background: #f7fafc; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
          <h2 style="color: #2d3748; margin-top: 0;">Message Details</h2>

          <div style="margin-bottom: 15px;">
            <strong style="color: #4a5568;">From:</strong><br/>
            <span style="color: #2d3748;">{name}</span>
          </div>

          <div style="margin-bottom: 15px;">
            <strong style="color: #4a5568;">Email:</strong><br/>
            <a href="mailto:{email}" style="color: #3b82f6;">{email}</a>
          </div>

          <div style="margin-bottom: 15px;">
            <strong style="color: #4a5568;">Subject:</strong><br/>
            <span style="color: #2d3748; font-weight: 600;">{subject}</span>
          </div>

          <div style="margin-bottom: 15px;">
            <strong style="color: #4a5568;">Message:</strong><br/>
            <p style="color: #2d3748; margin: 5px 0; padding: 15px; background: white; border-radius: 5px; white-space: pre-wrap; word-wrap: break-word;">
{message}
            </p>
          </div>
        </div>

        <div style="background: #eff6ff; padding: 15px; border-radius: 8px; border-left: 4px solid #3b82f6;">
          <p style="margin: 0; color: #1e3a8a; font-size: 13px;">
            <strong>Reply to this email</strong> to respond directly to {name} at {email}
          </p>
        </div>

        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e2e8f0; text-align: center; color: #a0aec0; font-size: 12px;">
          <p>This is an automated notification from Filter iCal Contact Form</p>
        </div>
      </body>
    </html>
    """

    text_body = f"""
New Contact Form Message - Filter iCal

From: {name}
Email: {email}
Subject: {subject}

Message:
{message}

---
Reply to this email to respond directly to {name} at {email}

This is an automated notification from Filter iCal Contact Form
    """

    return await _send_email(
        settings.admin_email,
        f"💬 Contact Form: {subject}",
        html_body,
        text_body,
        reply_to=email
    )
