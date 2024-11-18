from datetime import date


class ReportItem:
    loja: str
    nome: str
    categoria: str
    emissao: str
    vencimento: str
    departamento: str
    informacao: str
    val_titulo: float
    saldo: float

    def __init__(self, loja: str, nome: str, categoria: str, emissao: str, vencimento: str, departamento: str,
                 informacao: str, val_titulo: float,
                 saldo: float):
        self.loja = loja
        self.nome = nome
        self.categoria = categoria
        self.emissao = emissao
        self.vencimento = vencimento
        self.departamento = departamento
        self.informacao = informacao
        self.val_titulo = val_titulo
        self.saldo = saldo

    def __str__(self):
        return f"{self.loja}-{self.nome}-{self.categoria}-{self.emissao}-{self.vencimento}-{self.departamento}-{self.informacao}-{self.val_titulo}-{self.saldo}"

