from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

from customer_relationship.config import CustomerRelationshipConfig
from customer_relationship.emails import Email


class EmailSender:
    def __init__(self, config: CustomerRelationshipConfig) -> None:
        """
        Initialize configuration.

        Args:
            self: (todo): write your description
            config: (todo): write your description
        """
        self._config = config

    def send(self, recipient: str, email: Email) -> None:
        """
        Send an email.

        Args:
            self: (todo): write your description
            recipient: (str): write your description
            email: (str): write your description
        """
        with smtplib.SMTP(self._config.email_host, self._config.email_port) as server:
            server.login(self._config.email_username, self._config.email_password)
            msg = MIMEMultipart("alternative")
            msg["Subject"] = email.title
            msg["From"] = self._config.formatted_from
            msg["To"] = recipient
            msg.attach(MIMEText(email.text, "plain"))
            msg.attach(MIMEText(email.html, "html"))

            server.sendmail(self._config.formatted_from, recipient, msg.as_string())
