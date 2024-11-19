from uuid import UUID

import pandas as pd
from typing import Dict, Union

from app.domain.commands import Command
from app.domain.error import Error
from app.domain.handlers.command_handler import CommandHandler
from app.infra.services.oracle_data_extractor_service import OracleDataExtractorServiceService


class GeneratePDFReportCommand(Command):
    data: Dict[str, pd.DataFrame]


class GeneratePDFReportCommandHandler(CommandHandler):

    def __init__(self, data_extractor: OracleDataExtractorServiceService):
        self._data_extractor = data_extractor

    async def handler(self, command: GeneratePDFReportCommand) -> Union[UUID, Error]:
        result = await self._data_extractor.extract_data_to_report(command.data)

        if not isinstance(result, UUID):
            return Error(result)

        return result
