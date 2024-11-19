import asyncio
import datetime
import logging
import logging.config
import time
from apscheduler.schedulers.background import BackgroundScheduler
from tenacity import retry, stop_after_attempt, wait_fixed

from app.application.commands.email_send_command_handler import SendEmailCommand, SMTPServiceError
from app.application.commands.generate_pdf_report_command_handler import GeneratePDFReportCommand
from app.application.queries.load_report_data_query_handler import ReportDataQuery
from app.container import Container
from app.config.settings import Settings

logger = logging.getLogger('TelegramLog')
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


class App:

    def __init__(self):
        self.settings = Settings()  # Class With Env Vars Definitions
        self.container = Container()  # Container with dependencies definitions

        self.container.config.from_dict(self.settings.model_dump())
        self.send_email = self.container.send_email_handler()
        self.report_data_generator = self.container.report_data_generator()
        self.generate_pdf_report = self.container.generate_pdf_report()
        self.telegram_log = self.container.telegram_log_service()

        self.telegram_log.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.telegram_log.setLevel(logging.ERROR)
        logger.addHandler(self.telegram_log)

    async def run_app(self) -> None:
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

        # Query to get data
        res = await self.report_data_generator.handler(
            ReportDataQuery()
        )

        # Command to generate PDF
        await self.generate_pdf_report.handler(command=GeneratePDFReportCommand(
            data=res
        ))

        #Command to Send Email
        res = await self.send_email.handler(
            SendEmailCommand(
                sender=self.settings.SMTP_USERNAME,
                recipients=self.settings.SMTP_RECEIVERS.split(','),
                subject="Relatório Pagar - Dia " + datetime.datetime.now().strftime("%d-%m-%Y"),
                content=html,
                attach=None
            )
        )

        if isinstance(res, SMTPServiceError):
            logger.log(logging.ERROR, msg=res)

        logger.log(logging.INFO, msg=res)


async def main():
    app = App()
    await app.run_app()


@retry(stop=stop_after_attempt(5), wait=wait_fixed(10))
def job_send_mail():
    asyncio.run(main())


def job_send_mail_with_retries():
    try:
        job_send_mail()
    except Exception as e:
        logger.log(logging.ERROR, f"Envio de Email falhou após várias tentativas: {e}")


scheduler = BackgroundScheduler()

scheduler.add_job(job_send_mail_with_retries, 'cron', hour=8, minute=0)

scheduler.start()

try:
    logger.info("Aplicação Iniciada...")
    while True:
        time.sleep(1)
except (KeyboardInterrupt, SystemExit) as e:
    logger.error(f'O scheduler parou. Erro: {e}')
    scheduler.shutdown()
