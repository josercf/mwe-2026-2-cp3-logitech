"""CT18 (RF04): um tipo de cliente novo entra por registro, sem alterar os existentes."""
import unittest
from decimal import Decimal

from garantia.politica import Corporativo, Cortesia, PoliticaPorFaixas, Varejo
from garantia.registro import RegistroPoliticas, TipoClienteDesconhecido, registro_padrao


class RegistroPoliticasTest(unittest.TestCase):
    def test_registro_padrao_resolve_os_tres_tipos_existentes(self):
        registro = registro_padrao()
        self.assertIsInstance(registro.politica_para("VAREJO"), Varejo)
        self.assertIsInstance(registro.politica_para("CORPORATIVO"), Corporativo)
        self.assertIsInstance(registro.politica_para("CORTESIA"), Cortesia)

    def test_ct18_tipo_novo_e_registrado_sem_alterar_os_existentes(self):
        class Parceiro(PoliticaPorFaixas):
            def __init__(self):
                super().__init__(multiplicador=3, teto=Decimal("1000.00"))

        registro = registro_padrao()
        registro.registrar("PARCEIRO", Parceiro())

        self.assertEqual(
            registro.politica_para("PARCEIRO").calcular_credito(1441, Decimal("300.00")),
            Decimal("225.00"),
        )
        self.assertEqual(
            registro.politica_para("VAREJO").calcular_credito(1441, Decimal("300.00")),
            Decimal("75.00"),
        )

    def test_tipo_nao_registrado_e_rejeitado(self):
        with self.assertRaises(TipoClienteDesconhecido):
            RegistroPoliticas().politica_para("INEXISTENTE")


if __name__ == "__main__":
    unittest.main()
