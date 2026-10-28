"""Registro de políticas por tipo de cliente (RF04): um tipo novo é só um registro novo."""
from garantia.politica import Corporativo, Cortesia, Varejo


class TipoClienteDesconhecido(Exception):
    pass


class RegistroPoliticas:
    def __init__(self):
        self._politicas = {}

    def registrar(self, tipo_cliente: str, politica) -> None:
        self._politicas[tipo_cliente] = politica

    def politica_para(self, tipo_cliente: str):
        try:
            return self._politicas[tipo_cliente]
        except KeyError:
            raise TipoClienteDesconhecido(tipo_cliente) from None


def registro_padrao() -> RegistroPoliticas:
    registro = RegistroPoliticas()
    registro.registrar("VAREJO", Varejo())
    registro.registrar("CORPORATIVO", Corporativo())
    registro.registrar("CORTESIA", Cortesia())
    return registro
