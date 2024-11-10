from dependency_injector import containers, providers
from sqlalchemy.orm import Session

from email_context.app.email_send_command_handler import EmailSendCommandHandler
from email_context.database.sync_database import SyncDatabase
from email_context.infra.services.oracle_data_extractor_service import OracleDataExtractorService
from email_context.infra.services.smtp_mail_service import SMTPMailService


# Import other Contexts Here and Define dependencies inside the container

class Container(containers.DeclarativeContainer):
    __self__ = providers.Self()

    config = providers.Configuration()

    database: providers.Provider[SyncDatabase] = providers.Singleton(
        SyncDatabase, db_url=config.DATABASE_URL
    )

    mail_service: providers.Provider[SMTPMailService] = providers.Singleton(
        SMTPMailService,
        smtp_host=config.SMTP_HOST,
        smtp_port=config.SMTP_PORT,
        smtp_username=config.SMTP_USERNAME,
        smtp_password=config.SMTP_PASSWORD
    )

    oracle_data_extractor = providers.Factory(
        OracleDataExtractorService,
        database=database.provided
    )

    send_email_handler = providers.Factory(
        EmailSendCommandHandler,
        data_extractor=oracle_data_extractor,
        mail_service=mail_service
    )

#   example_context = providers.Factory(
#    ExampleContext,
#    db=database
#   )
