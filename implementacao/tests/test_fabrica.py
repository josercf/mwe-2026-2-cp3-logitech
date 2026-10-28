"""CT18 (RF04): a fábrica cria a estratégia de cada tipo de cliente; um tipo novo entra por
registro, sem alterar os existentes."""
import unittest
from decimal import Decimal

from garantia.fabrica import FabricaPoliticas, TipoClienteDesconhecido, fabrica_padrao
from garantia.politica import Corporativo, Cortesia, PoliticaPorFaixas, Varejo


class FabricaPoliticasTest(unittest.TestCase):
    def test_fabrica_padrao_cria_a_estrategia_dos_tres_tipos_existentes(self):
        fabrica = fabrica_padrao()
        self.assertIsInstance(fabrica.criar("VAREJO"), Varejo)
        self.assertIsInstance(fabrica.criar("CORPORATIVO"), Corporativo)
        self.assertIsInstance(fabrica.criar("CORTESIA"), Cortesia)

    def test_ct18_tipo_novo_e_registrado_sem_alterar_os_existentes(self):
        class Parceiro(PoliticaPorFaixas):
            def __init__(self):
                super().__init__(multiplicador=3, teto=Decimal("1000.00"))

        fabrica = fabrica_padrao()
        fabrica.registrar("PARCEIRO", Parceiro)

        self.assertEqual(
            fabrica.criar("PARCEIRO").calcular_credito(1441, Decimal("300.00")),
            Decimal("225.00"),
        )
        self.assertEqual(
            fabrica.criar("VAREJO").calcular_credito(1441, Decimal("300.00")),
            Decimal("75.00"),
        )

    def test_tipo_nao_registrado_e_rejeitado(self):
        with self.assertRaises(TipoClienteDesconhecido):
            FabricaPoliticas().criar("INEXISTENTE")


if __name__ == "__main__":
    unittest.main()
