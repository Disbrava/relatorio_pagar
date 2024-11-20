from datetime import datetime
from typing import List, Any

import pandas as pd
from sqlalchemy import text
from typing_extensions import Dict

from app.database.async_database import AsyncDatabase
from app.domain.report_item import ReportItem


class ReportRepository:

    def __init__(self, database: AsyncDatabase):
        self._database = database

    async def get_data_report_items(self, reference_date: datetime) -> Dict[str, pd.DataFrame]:
        sql = """SQL QUERY"""
        maraba = []
        nacional = []
        byd = []
        async with self._database.session_factory() as session:
            result = await session.execute(text(sql), {"reference_date": reference_date})
            rows = result.fetchall()

            if rows is not None and len(rows) > 0:
                for row in rows:
                    item = ReportItem(
                        loja=row[0],
                        nome=row[1],
                        categoria=row[2],
                        emissao=row[3],
                        vencimento=row[4],
                        departamento=row[5],
                        informacao=row[6],
                        val_titulo=row[7],
                        saldo=row[8]
                    )

                    if item.loja in ['1.1', '1.2']:
                        maraba.append(item.__dict__)
                    elif item.loja in ['2.1', '2.2', '2.4']:
                        nacional.append(item.__dict__)
                    elif item.loja in ['40.1']:
                        byd.append(item.__dict__)

        maraba = pd.DataFrame(maraba)[['loja', 'nome', 'categoria', 'emissao', 'saldo']]
        total_balance = pd.DataFrame([[maraba['saldo'].sum()]], columns=['saldo'])
        maraba = pd.concat([maraba, total_balance])
        maraba.columns = maraba.columns.map(lambda x: str(x).upper())

        nacional = pd.DataFrame(nacional)[['loja', 'nome', 'categoria', 'emissao', 'saldo']]
        total_balance = pd.DataFrame([[nacional['saldo'].sum()]], columns=['saldo'])
        nacional = pd.concat([nacional, total_balance])
        nacional.columns = nacional.columns.map(lambda x: str(x).upper())

        byd = pd.DataFrame(byd)[['loja', 'nome', 'categoria', 'emissao', 'saldo']]
        total_balance = pd.DataFrame([[byd['saldo'].sum()]], columns=['saldo'])
        byd = pd.concat([byd, total_balance])
        byd.columns = byd.columns.map(lambda x: str(x).upper())

        return {'MARABA': maraba, 'NACIONAL': nacional, 'BYD': byd}
