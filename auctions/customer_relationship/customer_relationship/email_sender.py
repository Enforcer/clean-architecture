import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


from customer_relationship.messages import Message
from customer_relationship.config import CustomerRelationshipConfig


class EmailSender:
    def __init__(self, config: CustomerRelationshipConfig) -> None:
        self._config = config

    def send(self, recipient: str, message: Message) -> None:
        with smtplib.SMTP(self._config.email_host, self._config.email_port) as server:
            server.login(self._config.email_username, self._config.email_password)
            msg = MIMEMultipart("alternative")
            msg["Subject"] = message.title
            msg["From"] = self._config.email_from
            msg["To"] = recipient
            msg.attach(MIMEText(message.text, "plain"))
            msg.attach(MIMEText(message.html, "html"))

            server.sendmail(self._config.email_from, recipient, msg.as_string())
