import smtplib
from email.mime.text import MIMEText

import inject

from application.configuration import Config
from application.interfaces import (
    Notification,
    NotificationsSender,
)


class PostmarkEmailSender(NotificationsSender):

    config: Config = inject.attr(Config)

    def send(self, notification: Notification):
        message = MIMEText(notification.contents)
        message['Subject'] = notification.title
        message['From'] = self.config.NOTIFICATIONS_FROM
        message['To'] = notification.recipient

        with smtplib.SMTP('smtp.postmarkapp.com', 25) as smtp_client:
            smtp_client.login(self.config.POSTMARK_TOKEN, self.config.POSTMARK_TOKEN)
            smtp_client.sendmail(message['From'], [message['To']], message.as_string())
