# Contexto do Projeto


Este projeto foi construído com o objetivo de realizar de forma automática uma solicitação de envio de informações em âmbito coporativo.
Foi solicitado que fosse enviado para o email de dois gestores um relatório analítico diário no qual constam todos os títulos a serem pagos com data de vencimento no dia vigente.


# Requisitos do Projeto 

   -  [x] Realizar conexão com banco de dados onde constam as informações dos títulos.
   -  [x] Montar um relatório a parter dos dados da consulta em  pdf
   -  [x] Enviar o arquivo com o relatório gerado para o email de dois gestores
   -  [x] Ambiente de Testes
   -  [x] Envio de logs de erro para o Telegram
   -  [x] Agendador de eventos para realizar a tarefa de envio de forma automática

# Ferramentas utilizadas

 - Python 3.8
 - Oracle Database
 - Pycharm IDE
 - Docker

# Bibliotecas e Frameworks fundamentais

 - Para operações com bancos de dados  [SQLAlchemy](https://www.sqlalchemy.org/)
 - Para agendamento de execução de jobs [APScheduler](https://pypi.org/project/APScheduler/)
 - Para tratamento de dados [Pandas](https://pandas.pydata.org/docs/index.html)
 - Para manipulaçao de arquivos pdf [Reportlab](https://docs.reportlab.com/)