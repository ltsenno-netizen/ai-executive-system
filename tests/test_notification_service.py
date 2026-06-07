import os
import sys
import unittest
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))

from app.services.notification_service import send_slack_alert, send_email_alert


class NotificationServiceTest(unittest.TestCase):
    @patch.dict(os.environ, {'SLACK_WEBHOOK_URL': 'https://example.com/webhook'})
    @patch('app.services.notification_service.requests.post')
    def test_send_slack_alert_uses_webhook(self, mock_post):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        send_slack_alert('Test alert')

        mock_post.assert_called_once_with(
            'https://example.com/webhook',
            json={'text': 'Test alert'},
            timeout=10,
        )
        mock_response.raise_for_status.assert_called_once()

    @patch.dict(
        os.environ,
        {
            'SMTP_HOST': 'smtp.example.com',
            'SMTP_PORT': '587',
            'SMTP_USERNAME': 'user',
            'SMTP_PASSWORD': 'pass',
            'EMAIL_FROM': 'sender@example.com',
            'EMAIL_TO': 'recipient@example.com',
            'SMTP_USE_TLS': 'true',
        },
    )
    @patch('app.services.notification_service.smtplib.SMTP')
    def test_send_email_alert_uses_smtp(self, mock_smtp):
        smtp_instance = mock_smtp.return_value.__enter__.return_value
        send_email_alert('Subject', 'Body content')

        smtp_instance.starttls.assert_called_once()
        smtp_instance.login.assert_called_once_with('user', 'pass')
        smtp_instance.send_message.assert_called_once()


if __name__ == '__main__':
    unittest.main()
