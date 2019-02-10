import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


from customer_relationship.messages import Message


class EmailSender:
    FROM = ("Auctions", "auctions@cleanarchitecture.io")  # TODO: shouldn't this be part of config, eh?

    def __init__(self, host: str, port: int, username: str, password: str) -> None:
        self._host = host
        self._port = port
        self._username = username
        self._password = password

    def send(self, recipient: str, message: Message) -> None:
        with smtplib.SMTP(self._host, self._port) as server:
            server.login(self._username, self._password)
            msg = MIMEMultipart("alternative")
            msg["Subject"] = message.title
            msg["From"] = self.FROM
            msg["To"] = recipient
            msg.attach(MIMEText(message.text, "plain"))
            msg.attach(MIMEText(message.html, "html"))

            server.sendmail(self.FROM, recipient, msg.as_string())
