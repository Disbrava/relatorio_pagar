import datetime
import os
from typing import Dict, Union
from uuid import UUID, uuid4

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Spacer, PageBreak
from reportlab.platypus import Table, TableStyle, Paragraph

from app.domain.services.data_extractor_interface import DataExtractorServiceInterface


class OracleDataExtractorServiceService(DataExtractorServiceInterface):
    def _transform_data_in_pdf_file(self, data: Dict[str, pd.DataFrame]) -> UUID:
        attach_name = f'Relatorio_Pagar_{str(datetime.datetime.now().day) + "_" + str(datetime.datetime.now().month) + "_" + str(datetime.datetime.now().year)}.pdf'
        if not os.path.exists('tmp'):
            os.makedirs('tmp')

        # Arquivo
        file_path = os.path.join('tmp', attach_name)
        pdf = SimpleDocTemplate(file_path, pagesize=landscape(A4))
        title = "Relatório de títulos a Pagar na Data  " + datetime.datetime.now().strftime("%d-%m-%Y")
        file_id = uuid4()
        elements = []
        styles = getSampleStyleSheet()
        #style_normal = styles["BodyText"]
        elements.append(Paragraph(f"{title.upper()}", styles['Title']))
        elements.append(Spacer(1, 20))

        for key, table in data.items():
            table = table.fillna('')
            table['SALDO'] = table['SALDO'].map('R$ {:,.2f}'.format)

            table_data = [table.columns.tolist()] + [[Paragraph(str(cell), styles['Normal']) for cell in row] for row in
                                                     table.values.tolist()]
            num_columns = len(table.columns)
            max_table_width = landscape(A4)[0] - 2 * inch  # Largura máxima da tabela com margens
            col_widths = [max_table_width / num_columns] * num_columns

            table = Table(table_data, colWidths=col_widths)
            last_row = len(table_data) - 1

            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Fundo do cabeçalho
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Cor do texto do cabeçalho
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Alinhamento central
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Fonte do cabeçalho
                ('FONTSIZE', (0, 0), (-1, -1), 9),  # Tamanho da fonte
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),  # Espaçamento inferior no cabeçalho
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),  # Cor de fundo das linhas
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),  # Linhas de grade
                ('BACKGROUND', (num_columns - 1, last_row), (num_columns - 1, last_row), colors.yellow),
                ('ALIGN', (num_columns - 1, last_row), (num_columns - 1, last_row), 'CENTER'),  # Alinhamento central
                ('FONTNAME', (num_columns - 1, last_row), (num_columns - 1, last_row), 'Helvetica-Bold'),
                ('FONTSIZE', (num_columns - 1, last_row), (num_columns - 1, last_row), 12),
                ('TEXTCOLOR', (num_columns - 1, last_row), (num_columns - 1, last_row), colors.black),
            ])
            table.setStyle(table_style)
            table.splitByRow = True  # Permite dividir a tabela em múltiplas páginas
            table.repeatRows = 1  # Número de linhas a serem repetidas (cabeçalho)

            subtitle = Paragraph(f"{str(key)}", styles['Heading2'])
            elements.append(subtitle)  # Adiciona o título
            elements.append(Spacer(1, 5))
            elements.append(table)  # Adiciona a tabela
            elements.append(Spacer(1, 20))  # Espaçamento entre tabelas
            elements.append(PageBreak())

        pdf.build(elements)

        return file_id

    async def extract_data_to_report(self, data: Dict[str, pd.DataFrame]) -> Union[UUID, str]:
        try:
            result = self._transform_data_in_pdf_file(data)
            return result
        except Exception as e:
            return f"Error: {e.__str__()}"
