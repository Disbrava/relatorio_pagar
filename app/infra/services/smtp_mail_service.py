import datetime
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.domain.email import Email
from app.domain.services.mail_service_interface import MailServiceInterface
from typing import Optional, Any
from email.message import EmailMessage
from email.mime.base import MIMEBase
from email import encoders


class SMTPMailService(MailServiceInterface):
    def __init__(
            self,
            smtp_host: str,
            smtp_port: int,
            smtp_username: Optional[str],
            smtp_password: Optional[str],
    ) -> None:
        self._smtp_host = smtp_host
        self._smtp_port = smtp_port
        self._smtp_username = smtp_username
        self._smtp_password = smtp_password

    def send_mail(self, email: Email) -> str:
        message: EmailMessage = self.__build_message(email)
        with smtplib.SMTP(self._smtp_host, self._smtp_port) as servidor_email:
            if os.getenv('ENVIRONMENT') == "TEST":
                servidor_email.sendmail(email.sender, email.recipients, message.as_string())
                return f"Email has Sent to Mailhog!"
            servidor_email.starttls()
            servidor_email.login(self._smtp_username, self._smtp_password)
            servidor_email.sendmail(email.sender, email.recipients, message.as_string())
            return f"Email has sent to Receivers!"

    def __build_message(self, email: Email) -> MIMEMultipart:
        message = MIMEMultipart()
        message["From"] = email.sender
        message["Subject"] = email.subject
        message["To"] = ", ".join(email.recipients)
        message.add_header("Content-Type", "text/html")

        message.attach(MIMEText(email.content, 'html'))

        attach_file_name_if_exists = f'Relatorio_Pagar_{str(datetime.datetime.now().day) + "_" + str(datetime.datetime.now().month) + "_" + str(datetime.datetime.now().year)}.pdf'

        if email.attach is not None:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(email.attach)
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{attach_file_name_if_exists}"')
            message.attach(part)

        return message
