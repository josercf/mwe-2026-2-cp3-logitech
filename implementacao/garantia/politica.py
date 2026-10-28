"""Política de Compensação da Garantia de Prazo (RF02, RF03 e RF04)."""
from decimal import ROUND_HALF_UP, Decimal

CENTAVO = Decimal("0.01")

# Limite superior inclusivo de cada faixa, em minutos, e o percentual do frete.
FAIXAS = (
    (120, Decimal("0")),
    (1440, Decimal("0.10")),
    (4320, Decimal("0.25")),
)
PERCENTUAL_ACIMA_DE_72H = Decimal("0.50")


def percentual_da_faixa(atraso_min: int) -> Decimal:
    for limite_min, percentual in FAIXAS:
        if atraso_min <= limite_min:
            return percentual
    return PERCENTUAL_ACIMA_DE_72H


class PoliticaPorFaixas:
    """Aplica as faixas do RF02 com um multiplicador e um teto por pedido."""

    def __init__(self, multiplicador: int, teto: Decimal):
        self.multiplicador = multiplicador
        self.teto = teto

    def calcular_credito(self, atraso_min: int, frete: Decimal) -> Decimal:
        percentual = percentual_da_faixa(atraso_min) * self.multiplicador
        credito = (frete * percentual).quantize(CENTAVO, ROUND_HALF_UP)
        return min(credito, self.teto)


class Varejo(PoliticaPorFaixas):
    def __init__(self):
        super().__init__(multiplicador=1, teto=Decimal("500.00"))


class Corporativo(PoliticaPorFaixas):
    def __init__(self):
        super().__init__(multiplicador=2, teto=Decimal("2000.00"))


class Cortesia:
    def calcular_credito(self, atraso_min: int, frete: Decimal) -> Decimal:
        return Decimal("0.00")
