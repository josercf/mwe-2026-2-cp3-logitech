"""Factory das estratégias de compensação (RF04): um tipo novo é só um registro novo."""
from garantia.politica import Corporativo, Cortesia, Varejo


class TipoClienteDesconhecido(Exception):
    pass


class FabricaPoliticas:
    def __init__(self):
        self._estrategias = {}

    def registrar(self, tipo_cliente: str, estrategia: type) -> None:
        self._estrategias[tipo_cliente] = estrategia

    def criar(self, tipo_cliente: str):
        try:
            return self._estrategias[tipo_cliente]()
        except KeyError:
            raise TipoClienteDesconhecido(tipo_cliente) from None


def fabrica_padrao() -> FabricaPoliticas:
    fabrica = FabricaPoliticas()
    fabrica.registrar("VAREJO", Varejo)
    fabrica.registrar("CORPORATIVO", Corporativo)
    fabrica.registrar("CORTESIA", Cortesia)
    return fabrica
