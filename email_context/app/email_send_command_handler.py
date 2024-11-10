import os
from datetime import datetime
from typing import Any, List, Optional

from email_context.domain.commands import Command
from email_context.domain.email import Email
from email_context.domain.error import Error
from email_context.domain.handlers.command_handler import CommandHandler
from email_context.infra.services.oracle_data_extractor_service import OracleDataExtractorService
from email_context.infra.services.smtp_mail_service import SMTPMailService


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

    def __init__(self, data_extractor: OracleDataExtractorService, mail_service: SMTPMailService) -> [str,
                                                                                                      SMTPServiceError]:
        self._data_extractor = data_extractor
        self._mail_service = mail_service

    def handler(self, command: SendEmailCommand) -> Any:
        html = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório de Pagamentos</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 20px;
            background-color: #f9f9f9;
            color: #333;
        }
        h1 {
            color: #00000;
        }
        p {
            margin: 10px 0;
        }
        .footer {
            margin-top: 20px;
            font-size: 0.9em;
            color: #777;
        }
        .highlight {
            background-color: #e7f3fe;
            padding: 10px;
            border-left: 6px solid #2196F3;
        }
    </style>
</head>
<body>

     <h3>Olá Controle do Pagar,</h3>
    
    <div >
        <p>Segue em anexo o relatório com todos os valores a serem pagos na data atual.</p>
    </div>
    <br/>    
	<p>Atenciosamente,</p>
    <p><strong>Fabrício Silva Sales</strong></p>
    
    <div class="footer">
        <p>Este email foi gerado automaticamente.</p>
    </div>

</body>
</html>
"""

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
