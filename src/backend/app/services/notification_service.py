import logging
import os
import smtplib
import ssl
from email.message import EmailMessage

import requests

logger = logging.getLogger(__name__)


def send_slack_alert(message: str) -> None:
    """Send a Slack alert through a webhook or API client."""
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    if not webhook_url:
        logger.warning('SLACK_WEBHOOK_URL is not configured. Logging Slack alert only.')
        logger.info('Slack alert: %s', message)
        return

    payload = {'text': message}
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        logger.info('Slack alert sent successfully to %s', webhook_url)
    except Exception as exc:
        logger.error('Failed to send Slack alert: %s', exc, exc_info=True)
        raise


def send_email_alert(subject: str, body: str) -> None:
    """Send an email alert through SMTP or provider API."""
    smtp_host = os.getenv('SMTP_HOST')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_PASSWORD')
    email_from = os.getenv('EMAIL_FROM')
    email_to = os.getenv('EMAIL_TO')
    use_tls = os.getenv('SMTP_USE_TLS', 'true').lower() in {'1', 'true', 'yes'}

    if not smtp_host or not email_from or not email_to:
        logger.warning('SMTP settings are incomplete. Logging email alert only.')
        logger.info('Email alert subject: %s\n%s', subject, body)
        return

    message = EmailMessage()
    message['Subject'] = subject
    message['From'] = email_from
    message['To'] = email_to
    message.set_content(body)

    recipients = [recipient.strip() for recipient in email_to.split(',') if recipient.strip()]

    try:
        if use_tls:
            context = ssl.create_default_context()
            with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
                server.starttls(context=context)
                if smtp_username and smtp_password:
                    server.login(smtp_username, smtp_password)
                server.send_message(message, from_addr=email_from, to_addrs=recipients)
        else:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
                if smtp_username and smtp_password:
                    server.login(smtp_username, smtp_password)
                server.send_message(message, from_addr=email_from, to_addrs=recipients)

        logger.info('Email alert sent successfully to %s', email_to)
    except Exception as exc:
        logger.error('Failed to send email alert: %s', exc, exc_info=True)
        raise
