from datetime import datetime
from typing import List, Dict
from uuid import uuid4
import pandas as pd
from pydantic import Field
from sqlalchemy import text

from email_context.database.async_database import AsyncDatabase
from email_context.domain.handlers.query_handler import QueryHandler
from email_context.domain.query import Query
from email_context.domain.report_item import ReportItem


class ReportDataQuery(Query):
    id: uuid4 = Field(default_factory=uuid4)
    reference_date: datetime = Field(default_factory=datetime.today)


class ReportDataLoadQueryHandler(QueryHandler):

    def __init__(self, database: AsyncDatabase):
        self._database = database

    async def handler(self, query: ReportDataQuery) -> Dict[str, pd.DataFrame]:
        sql = """
                WITH dw AS (
                SELECT DISTINCT
                        	A.CLIENTE,
                        	A.NOME,
                        	B.EMPRESA,
                        	B.REVENDA,
                        	B.TITULO,
                        	B.VAL_TITULO,
                        	B.DTA_EMISSAO,
                        	B.DTA_VENCIMENTO,
                        	B.STATUS,
                        	B.DEPARTAMENTO,
                        	B.ORIGEM,
                        	B.TIPO,
                        	(
                                SELECT
                                    FO.DES_ORIGEM
                                FROM
                                    CNP.FIN_ORIGEM FO
                                WHERE
                                    FO.ORIGEM = B.ORIGEM
                                    AND FO.EMPRESA = B.EMPRESA
                                    AND FO.REVENDA = B.REVENDA
                                GROUP BY
                                    FO.DES_ORIGEM
                            ) DES_ORIGEM,
                            B.PAGAR_RECEBER,
                            B.BANCO,
                            (
                                SELECT DES_BANCO FROM CNP.FIN_BANCO 
                                WHERE CNP.FIN_BANCO.BANCO=B.BANCO 
                                AND CNP.FIN_BANCO.EMPRESA = B.EMPRESA 
                                AND CNP.FIN_BANCO.REVENDA = B.REVENDA
                            ) DES_BANCO,
                            CASE
                                WHEN B.STATUS = 'CA' THEN 0
                                ELSE (
                                    B.VAL_TITULO - (
                                        COALESCE(
                                            (
                                                SELECT
                                                    SUM(CNP.FIN_TITULO_PAGAMENTO.VAL_PAGAMENTO)
                                                FROM
                                                    CNP.FIN_TITULO_PAGAMENTO
                                                WHERE
                                                    CNP.FIN_TITULO_PAGAMENTO.EMPRESA = B.EMPRESA
                                                    AND CNP.FIN_TITULO_PAGAMENTO.REVENDA = B.REVENDA
                                                    AND CNP.FIN_TITULO_PAGAMENTO.TITULO = B.TITULO
                                                    AND CNP.FIN_TITULO_PAGAMENTO.DUPLICATA = B.DUPLICATA
                                                    AND CNP.FIN_TITULO_PAGAMENTO.CLIENTE = B.CLIENTE
                                                    AND CNP.FIN_TITULO_PAGAMENTO.TIPO = B.TIPO
                                            ),
                                            0
                                        ) + COALESCE(
                                            (
                                                SELECT
                                                    SUM(CNP.FIN_DEVOLUCAO.VAL_DEVOLUCAO)
                                                FROM
                                                    CNP.FIN_DEVOLUCAO
                                                WHERE
                                                    CNP.FIN_DEVOLUCAO.EMPRESA = B.EMPRESA
                                                    AND CNP.FIN_DEVOLUCAO.REVENDA = B.REVENDA
                                                    AND CNP.FIN_DEVOLUCAO.TITULO = B.TITULO
                                                    AND CNP.FIN_DEVOLUCAO.DUPLICATA = B.DUPLICATA
                                                    AND CNP.FIN_DEVOLUCAO.CLIENTE = B.CLIENTE
                                                    AND CNP.FIN_DEVOLUCAO.TIPO = B.TIPO
                                            ),
                                            0
                                        )
                                    )
                                )
                            END SALDO,
                            (
                                COALESCE(
                                    (
                                        SELECT
                                            MAX(CNP.FIN_TITULO_PAGAMENTO.DTA_PAGAMENTO)
                                        FROM
                                            CNP.FIN_TITULO_PAGAMENTO
                                        WHERE
                                            CNP.FIN_TITULO_PAGAMENTO.EMPRESA = B.EMPRESA
                                            AND CNP.FIN_TITULO_PAGAMENTO.REVENDA = B.REVENDA
                                            AND CNP.FIN_TITULO_PAGAMENTO.TITULO = B.TITULO
                                            AND CNP.FIN_TITULO_PAGAMENTO.DUPLICATA = B.DUPLICATA
                                            AND CNP.FIN_TITULO_PAGAMENTO.CLIENTE = B.CLIENTE
                                            AND CNP.FIN_TITULO_PAGAMENTO.TIPO = B.TIPO
                                            AND B.STATUS <> 'DE'
                                            AND B.STATUS <> 'CA'
                                            AND B.STATUS <> 'EM'
                                            AND CNP.FIN_TITULO_PAGAMENTO.NRO_PAGAMENTO = (
                                                SELECT
                                                    MAX(CNP.FIN_TITULO_PAGAMENTO.NRO_PAGAMENTO)
                                                FROM
                                                    CNP.FIN_TITULO_PAGAMENTO
                                                WHERE
                                                    CNP.FIN_TITULO_PAGAMENTO.EMPRESA = B.EMPRESA
                                                    AND CNP.FIN_TITULO_PAGAMENTO.REVENDA = B.REVENDA
                                                    AND CNP.FIN_TITULO_PAGAMENTO.TITULO = B.TITULO
                                                    AND CNP.FIN_TITULO_PAGAMENTO.DUPLICATA = B.DUPLICATA
                                                    AND CNP.FIN_TITULO_PAGAMENTO.CLIENTE = B.CLIENTE
                                                    AND CNP.FIN_TITULO_PAGAMENTO.TIPO = B.TIPO
                                            )
                                    ),
                                    NULL
                                )
                            ) DTA_PAGAMENTO,
                            (
                        	SELECT
                        		G.DES_GRUPO_CLIENTE
                        	FROM
                        		CNP.FAT_GRUPO_CLIENTE G
                        	WHERE
                        		G.GRUPO_CLIENTE = A.GRUPO_CLIENTE
                            ) DES_GRUPO_CLIENTE,
                        	SUBSTR(B.HISTORICO, 1, 200) HISTORICO,
                        	(
                        	SELECT
                        		MAX(CPR.DES_PROVIDENCIA)
                        	FROM
                        		CNP.CAC_CONTATO CCO, 
                        		CNP.CAC_PROVIDENCIA CPR,
                        		CNP.GER_USUARIO GUS
                        		WHERE
                        		CCO.EMPRESA = B.EMPRESA
                        		AND CCO.REVENDA = B.REVENDA
                        		AND CCO.TITULO = B.TITULO
                        		AND CCO.DUPLICATA = B.DUPLICATA
                        		AND CCO.CLIENTE = B.CLIENTE
                        		AND CCO.TIPO_DUPLICATA = B.TIPO		
                        		AND CPR.EMPRESA = CCO.EMPRESA
                        		AND CPR.REVENDA = CCO.REVENDA
                        		AND CPR.CONTATO = CCO.CONTATO
                        		AND CPR.PROVIDENCIA = (
                        		SELECT
                        			MAX(CPR1.PROVIDENCIA)
                        		FROM
                        			CNP.CAC_PROVIDENCIA CPR1
                        		WHERE
                        			CPR1.EMPRESA = CPR.EMPRESA
                        			AND CPR1.REVENDA = CPR.REVENDA
                        			AND CPR1.CONTATO = CPR.CONTATO
                                 ) 
                                 AND GUS.USUARIO = CPR.USUARIO
                        	) INFORMACOES,
                        	B.TIPO_ITEM
                        FROM
                        	CNP.FAT_CLIENTE A
                        INNER JOIN (
                        	SELECT
                        		CNP.FIN_TITULO.EMPRESA,
                        		CNP.FIN_TITULO.REVENDA,
                        		CNP.FIN_TITULO.TITULO,
                        		CNP.FIN_TITULO.DUPLICATA,
                        		CNP.FIN_TITULO.CLIENTE,
                        		CNP.FIN_TITULO.OPERACAO,
                        		CNP.FIN_TITULO.TIPO,
                        		CNP.FIN_TITULO.BANCO,
                        		CNP.FIN_TITULO.HISTORICO,
                        		CNP.FIN_TITULO.VAL_TITULO,
                        		CNP.FIN_TITULO.PAGAR_RECEBER,
                        		CNP.FIN_TITULO.DTA_EMISSAO,
                        		CNP.FIN_TITULO.DTA_VENCIMENTO,
                        		CNP.FIN_TITULO.STATUS,
                        		CNP.FIN_TITULO.DEPARTAMENTO,
                        		CNP.FIN_TITULO.ORIGEM,
                        		CNP.FIN_TITULO.PLANO_CONTRATO,
                        		CNP.FIN_TITULO.TIPO_ITEM,
                        		CNP.FIN_TITULO.USUARIO,
                        		CNP.FIN_TITULO.PROPOSTA,
                        		CNP.FIN_TITULO.LOCALIZACAO
                        	FROM
                        		CNP.FIN_TITULO
                         ) B ON
                        	(B.CLIENTE = A.CLIENTE)
                        LEFT JOIN CNP.FAT_MOVIMENTO_CAPA FMC ON
                        	(
                                FMC.EMPRESA = B.EMPRESA
                        		AND FMC.REVENDA = B.REVENDA
                        		AND FMC.OPERACAO = B.OPERACAO
                         )
                        LEFT JOIN CNP.VEI_PROPOSTA VP ON
                        	(
                                VP.EMPRESA = FMC.EMPRESA
                        		AND VP.REVENDA = FMC.REVENDA
                        		AND VP.CONTATO = FMC.CONTATO
                            )
                        LEFT JOIN CNP.VEI_AVALIACAO_PROPOSTA AVP ON
                        	(
                                AVP.EMPRESA = B.EMPRESA
                        		AND AVP.REVENDA = B.REVENDA
                        		AND AVP.PROPOSTA = VP.PROPOSTA
                            )
                        LEFT JOIN CNP.VEI_AVALIACAO AV ON
                        	(
                                AV.EMPRESA = AVP.EMPRESA
                        		AND AVP.AVALIACAO = AV.AVALIACAO
                            )
                        LEFT JOIN CNP.FAT_PESSOA_FISICA PF ON
                        	PF.CLIENTE = A.CLIENTE
                        LEFT JOIN CNP.FAT_PESSOA_JURIDICA PJ ON
                        	PJ.CLIENTE = A.CLIENTE
                        WHERE
                            B.TIPO IN ('CP')
                        	AND B.STATUS IN ('EM', 'PP')
                        	--AND B.ORIGEM IN (10334, 80160)
                        ORDER BY
                        	A.NOME,
                        	B.TITULO)


                SELECT 
                (dw.EMPRESA ||'.'|| dw.REVENDA) loja,
                dw.NOME,

                (CASE
                WHEN dw.ORIGEM IN (20128, 20130, 20134, 20136, 20146, 20151, 20155,20157, 20666, 20668) THEN 'Empréstimo'
                WHEN dw.ORIGEM IN (20261,20262,20264,20282,20283,20284,20285,20286,20287,20288,20289, 20290,20291,20292,20293,20294,20297,20298,20299,20300,20301) THEN  'Imposto' 
                WHEN dw.ORIGEM IN (20005) THEN 'Clientes'
                WHEN dw.ORIGEM IN (20004,20006,20009,20660,80045,90077,90091,90092) THEN 'Fábrica'
                WHEN dw.ORIGEM IN (20202, 20219) THEN 'Fornecedor'
                WHEN dw.ORIGEM IN (90006,90007,90008,90029,90031,90032,90033,90034,90037,90038,90260) THEN 'Vendas'
                ELSE 'Outros'
                END) categoria,

                TO_CHAR(dw.DTA_EMISSAO, 'DD/MM/YYYY') EMISSAO,
                TO_CHAR(dw.DTA_VENCIMENTO,'DD/MM/YYYY') VENCIMENTO,
                (
                SELECT 
                gd.NOME
                FROM CNP.GER_DEPARTAMENTO gd 
                WHERE 
                gd.EMPRESA=dw.EMPRESA AND 
                gd.REVENDA=dw.REVENDA AND
                gd.DEPARTAMENTO=dw.DEPARTAMENTO
                ) DEPARTAMENTO,
                COALESCE(dw.INFORMACOES,'-') INFORMACAO,
                dw.VAL_TITULO,
                dw.SALDO


                FROM dw 

                WHERE trunc(dw.DTA_VENCIMENTO) = trunc(:reference_date)
                """
        maraba = []
        nacional = []
        byd = []

        async with self._database.session_factory() as session:
            result = await session.execute(text(sql), {"reference_date": query.reference_date})

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
