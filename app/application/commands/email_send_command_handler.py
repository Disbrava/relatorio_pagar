import os
from datetime import datetime
from typing import Any, List, Optional, Union

from app.domain.commands import Command
from app.domain.email import Email
from app.domain.error import Error
from app.domain.handlers.command_handler import CommandHandler
from app.infra.services.oracle_data_extractor_service import OracleDataExtractorServiceService
from app.infra.services.smtp_mail_service import SMTPMailService


class SendEmailCommand(Command):
    sender: str
    recipients: List[str]
    subject: str
    content: str
    attach: Optional[bytes] = None


class SMTPServiceError(Error):
    def __init__(self, message):
        super().__init__(message)

    def __str__(self):
        return f"SMTPServiceError: {self.message}"


class SendEmailCommandHandler(CommandHandler):

    def __init__(self, mail_service: SMTPMailService) -> [str, SMTPServiceError]:
        self._mail_service = mail_service

    async def handler(self, command: SendEmailCommand) -> Union[str, SMTPServiceError]:

        email = Email(
            sender=command.sender,
            recipients=command.recipients,
            subject=command.subject,
            content=command.content,
            attach=command.attach
        )
        attach_name = f'Relatorio_Pagar_{str(datetime.now().day) + "_" + str(datetime.now().month) + "_" + str(datetime.now().year)}.pdf'

        directory = os.path.join('tmp')
        file_path = os.path.join(os.path.abspath(directory), attach_name)

        with open(file_path, 'rb') as file:
            email.attach = file.read()

        res = self._mail_service.send_mail(email)

        if isinstance(res, SMTPServiceError):
            SMTPServiceError(res.__str__())

        os.remove(file_path)
        return res
