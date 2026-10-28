# 5. Implementação em TDD

Implementem a regra de cálculo do crédito (RF02, RF03 e RF04) em **uma** linguagem à
escolha da dupla: Java, C#, Python ou TypeScript. O Codespace deste repositório já traz
as quatro.

## Como trabalhar

1. Escrevam um teste para um caso do plano (`docs/03-testes.md`) e confirmem que ele
   **falha**. Façam o commit: `test: CT01 atraso abaixo da tolerância não gera crédito`.
2. Escrevam o mínimo de código que faz o teste passar. Façam o commit:
   `feat: calcula crédito zero dentro da tolerância`.
3. Se for preciso, refatorem com os testes passando. Façam o commit: `refactor: ...`.
4. Repitam para o próximo caso.

O histórico de commits é a evidência do TDD: o commit de teste vem antes do commit de
código que o faz passar.

## O que registrar aqui

- Linguagem e framework de teste: Python 3 com `unittest` (biblioteca padrão, sem dependências)
- Comando para executar os testes (a partir da pasta `implementacao/`): `python3 -m unittest -v`
- Casos do plano implementados (IDs): CT01 a CT14, CT17 (parte do crédito; a publicação de `AtrasoConstatado` é do
  agregado `Garantia`, fora da regra de cálculo) e CT18
- Estrutura:
  - `garantia/politica.py`: Strategy da Política de Compensação. `PoliticaPorFaixas` aplica as
    faixas do RF02 com multiplicador e teto; `Varejo`, `Corporativo` e `Cortesia` são as
    estratégias de cada tipo de cliente (RF02 e RF03)
  - `garantia/registro.py`: registro de políticas por tipo de cliente. Um tipo novo é só um
    `registrar(...)` novo, sem alterar as classes existentes (RF04)
- Saída da última execução dos testes:

```
test_ct09_atraso_de_2h01_gera_20_por_cento ... ok
test_ct10_atraso_de_24h01_gera_50_por_cento ... ok
test_ct11_atraso_de_72h01_gera_100_por_cento ... ok
test_ct12_credito_exatamente_no_teto_de_2000 ... ok
test_ct13_credito_acima_do_teto_e_limitado_a_2000 ... ok
test_ct17_cortesia_nao_recebe_credito_mesmo_com_atraso_de_30h ... ok
test_ct01_atraso_de_2h00_nao_gera_credito ... ok
test_ct02_atraso_de_2h01_gera_10_por_cento ... ok
test_ct03_atraso_de_24h00_ainda_gera_10_por_cento ... ok
test_ct04_atraso_de_24h01_gera_25_por_cento ... ok
test_ct05_atraso_de_72h00_ainda_gera_25_por_cento ... ok
test_ct06_atraso_de_72h01_gera_50_por_cento ... ok
test_ct07_credito_exatamente_no_teto_de_500 ... ok
test_ct08_credito_acima_do_teto_e_limitado_a_500 ... ok
test_ct14_credito_arredondado_half_up_para_centavos ... ok
test_ct18_tipo_novo_e_registrado_sem_alterar_os_existentes ... ok
test_registro_padrao_resolve_os_tres_tipos_existentes ... ok
test_tipo_nao_registrado_e_rejeitado ... ok

----------------------------------------------------------------------
Ran 18 tests in 0.001s

OK
```
