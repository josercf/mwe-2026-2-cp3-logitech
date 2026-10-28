"""Casos do plano de testes (docs/03-testes.md) para a Política de Compensação."""
import unittest
from decimal import Decimal

from garantia.politica import Corporativo, Cortesia, Varejo


class VarejoTest(unittest.TestCase):
    def setUp(self):
        self.politica = Varejo()

    def test_ct01_atraso_de_2h00_nao_gera_credito(self):
        self.assertEqual(self.politica.calcular_credito(120, Decimal("300.00")), Decimal("0.00"))

    def test_ct02_atraso_de_2h01_gera_10_por_cento(self):
        self.assertEqual(self.politica.calcular_credito(121, Decimal("300.00")), Decimal("30.00"))

    def test_ct03_atraso_de_24h00_ainda_gera_10_por_cento(self):
        self.assertEqual(self.politica.calcular_credito(1440, Decimal("300.00")), Decimal("30.00"))

    def test_ct04_atraso_de_24h01_gera_25_por_cento(self):
        self.assertEqual(self.politica.calcular_credito(1441, Decimal("300.00")), Decimal("75.00"))

    def test_ct05_atraso_de_72h00_ainda_gera_25_por_cento(self):
        self.assertEqual(self.politica.calcular_credito(4320, Decimal("300.00")), Decimal("75.00"))

    def test_ct06_atraso_de_72h01_gera_50_por_cento(self):
        self.assertEqual(self.politica.calcular_credito(4321, Decimal("300.00")), Decimal("150.00"))

    def test_ct07_credito_exatamente_no_teto_de_500(self):
        self.assertEqual(self.politica.calcular_credito(4321, Decimal("1000.00")), Decimal("500.00"))

    def test_ct08_credito_acima_do_teto_e_limitado_a_500(self):
        self.assertEqual(self.politica.calcular_credito(4321, Decimal("1000.02")), Decimal("500.00"))

    def test_ct14_credito_arredondado_half_up_para_centavos(self):
        credito = self.politica.calcular_credito(121, Decimal("33.35"))
        self.assertEqual(credito, Decimal("3.34"))
        self.assertEqual(credito.as_tuple().exponent, -2)


class CorporativoTest(unittest.TestCase):
    def setUp(self):
        self.politica = Corporativo()

    def test_ct09_atraso_de_2h01_gera_20_por_cento(self):
        self.assertEqual(self.politica.calcular_credito(121, Decimal("300.00")), Decimal("60.00"))

    def test_ct10_atraso_de_24h01_gera_50_por_cento(self):
        self.assertEqual(self.politica.calcular_credito(1441, Decimal("300.00")), Decimal("150.00"))

    def test_ct11_atraso_de_72h01_gera_100_por_cento(self):
        self.assertEqual(self.politica.calcular_credito(4321, Decimal("300.00")), Decimal("300.00"))

    def test_ct12_credito_exatamente_no_teto_de_2000(self):
        self.assertEqual(self.politica.calcular_credito(4321, Decimal("2000.00")), Decimal("2000.00"))

    def test_ct13_credito_acima_do_teto_e_limitado_a_2000(self):
        self.assertEqual(self.politica.calcular_credito(4321, Decimal("2000.02")), Decimal("2000.00"))


class CortesiaTest(unittest.TestCase):
    def test_ct17_cortesia_nao_recebe_credito_mesmo_com_atraso_de_30h(self):
        # A publicação de AtrasoConstatado (CT17) é do agregado Garantia, fora da Política de Compensação.
        self.assertEqual(Cortesia().calcular_credito(1800, Decimal("0.00")), Decimal("0.00"))


if __name__ == "__main__":
    unittest.main()
