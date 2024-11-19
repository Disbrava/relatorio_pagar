from datetime import datetime
from typing import Dict
from uuid import uuid4

import pandas as pd
from pydantic import Field

from app.data.report_repository import ReportRepository
from app.domain.handlers.query_handler import QueryHandler
from app.domain.query import Query


class ReportDataQuery(Query):
    id: uuid4 = Field(default_factory=uuid4)
    reference_date: datetime = Field(default_factory=datetime.today)


class ReportDataLoadQueryHandler(QueryHandler):

    def __init__(self, report_repository: ReportRepository):
        self._repo = report_repository

    async def handler(self, query: ReportDataQuery) -> Dict[str, pd.DataFrame]:
        result = await self._repo.get_data_report_items(reference_date=query.reference_date)
        return result

