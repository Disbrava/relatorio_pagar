from dependency_injector import containers, providers

from app.application.commands.email_send_command_handler import SendEmailCommandHandler
from app.application.commands.generate_pdf_report_command_handler import GeneratePDFReportCommandHandler
from app.application.queries.load_report_data_query_handler import ReportDataLoadQueryHandler
from app.data.report_repository import ReportRepository
from app.database.async_database import AsyncDatabase
from app.infra.services.oracle_data_extractor_service import OracleDataExtractorServiceService
from app.infra.services.smtp_mail_service import SMTPMailService
from app.infra.services.telegram_log_service import TelegramLogService


class Container(containers.DeclarativeContainer):
    __self__ = providers.Self()

    # Config Env Vars
    config = providers.Configuration()

    # Provide Database Instance
    async_database: providers.Provider[AsyncDatabase] = providers.Singleton(
        AsyncDatabase, db_url=config.DATABASE_URL
    )

    report_repo = providers.Factory(
        ReportRepository,
        database=async_database
    )

    oracle_data_extractor = providers.Factory(
        OracleDataExtractorServiceService

    )

    # Services
    telegram_log_service = providers.Factory(
        TelegramLogService,
        api_url=config.TELEGRAM_API_URL,
        bot_token=config.BOT_TOKEN,
        chat_id=config.CHAT_ID
    )

    mail_service: providers.Provider[SMTPMailService] = providers.Singleton(
        SMTPMailService,
        smtp_host=config.SMTP_HOST,
        smtp_port=config.SMTP_PORT,
        smtp_username=config.SMTP_USERNAME,
        smtp_password=config.SMTP_PASSWORD
    )

    #Commands
    send_email_handler = providers.Factory(
        SendEmailCommandHandler,
        mail_service=mail_service
    )

    generate_pdf_report = providers.Factory(
        GeneratePDFReportCommandHandler,
        data_extractor=oracle_data_extractor
    )

    # Query
    report_data_generator = providers.Factory(
        ReportDataLoadQueryHandler,
        report_repository=report_repo
    )
