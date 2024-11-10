from uuid import UUID

import pandas as pd
from typing import Dict, Union

from email_context.domain.commands import Command
from email_context.domain.error import Error
from email_context.domain.handlers.command_handler import CommandHandler
from email_context.infra.services.oracle_data_extractor_service import OracleDataExtractorService


class GeneratePDFReportCommand(Command):
    data: Dict[str, pd.DataFrame]


class GeneratePDFReportCommandHandler(CommandHandler):

    def __init__(self, data_extractor: OracleDataExtractorService):
        self._data_extractor = data_extractor

    def handler(self, command: GeneratePDFReportCommand) -> Union[UUID, Error]:
        result = self._data_extractor.extract_data_to_report(command.data)

        if not isinstance(result, UUID):
            return Error(result)

        return result
