import asyncio
import datetime
import logging
import logging.config
import uuid

from email_context.app.email_send_command_handler import SendEmailCommand, SMTPServiceError
from email_context.app.generate_pdf_report_command_handler import GeneratePDFReportCommand
from email_context.app.load_report_data_query_handler import ReportDataQuery
from email_context.container import Container
from email_context.config.settings import Settings

logging.config.fileConfig('../logging.ini')

logger = logging.getLogger('root')


class App:

    def __init__(self):
        self.settings = Settings()  # Class With Env Vars Definitions
        self.container = Container()  # Container with dependencies definitions

        self.container.config.from_dict(self.settings.model_dump())
        self.send_email = self.container.send_email_handler()
        self.report_data_generator = self.container.report_data_generator()
        self.generate_pdf_report = self.container.generate_pdf_report()

    async def run_app(self):

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
        command = SendEmailCommand(
            sender=self.settings.SMTP_USERNAME,
            recipients=self.settings.SMTP_RECEIVERS.split(','),
            subject="Relatório Pagar - Dia " + datetime.datetime.now().strftime("%d-%m-%Y"),
            content=html,
            attach=None
        )

        query = ReportDataQuery()

        res = await self.report_data_generator.handler(query)

        self.generate_pdf_report.handler(command=GeneratePDFReportCommand(
            data=res
        ))

        res = self.send_email.handler(
            command
        )

        if isinstance(res, SMTPServiceError):
            logger.log(logging.ERROR, res)

        logger.log(logging.INFO, res)


async def main():
    app = App()
    await app.run_app()


if __name__ == "__main__":
    asyncio.run(main())
