# 3. Plano de testes

## Pirâmide de testes

A regra de crédito é essencialmente matemática e deve ser validada em massa por testes de unidade. A integração é importante para validar contratos entre serviços e a ponta a ponta é sparsa, porque o objetivo é garantir o comportamento do negócio e a correção das interfaces, sem inflar custos de execução.

| Nível | Quantidade de casos | O que cobre |
|---|---|---|
| Unidade | 8 | Cálculo do crédito por tipo de cliente, limites, ausência comprovada e deduplicação do evento. |
| Integração | 3 | Comunicação entre Garantia, Faturamento, Telemetria e Notificações. |
| Ponta a ponta | 2 | Fluxo principal de entrega atrasada e o portal com atualização ao vivo. |

## Casos de teste

| ID | Requisito | Pré-condição | Entrada | Resultado esperado | Nível | Dublê | Justificativa do dublê |
|---|---|---|---|---|---|---|---|
| CT01 | RF02 | Cliente Varejo, frete de R$ 300,00 | Atraso de 1h59 | Crédito de R$ 0,00 | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT02 | RF02 | Cliente Varejo, frete de R$ 300,00 | Atraso de 2h01 | Crédito de R$ 30,00 (10% de R$ 300,00) | Unidade | Nenhum | A regra de percentuais precisa ser testada em limite exato |
| CT03 | RF02 | Cliente Varejo, frete de R$ 1.000,00 | Atraso de 24h00 | Crédito de R$ 250,00 (25% de R$ 1.000,00) | Unidade | Nenhum | Valida o limite inferior do segundo intervalo |
| CT04 | RF02 | Cliente Varejo, frete de R$ 800,00 | Atraso de 72h01 | Crédito de R$ 400,00 (50% de R$ 800,00) | Unidade | Nenhum | Verifica o limite superior do intervalo maior |
| CT05 | RF02 | Cliente Varejo, frete de R$ 10.000,00 | Atraso de 120h | Crédito máximo de R$ 500,00 | Unidade | Nenhum | Garante o teto financeiro de Varejo |
| CT06 | RF03 | Cliente Corporativo, frete de R$ 1.000,00 | Atraso de 3h | Crédito de R$ 200,00 (20% de R$ 1.000,00) | Unidade | Nenhum | Verifica duplicação dos percentuais do cliente corporativo |
| CT07 | RF03 | Cliente Corporativo, frete de R$ 10.000,00 | Atraso de 90h | Crédito máximo de R$ 2.000,00 | Unidade | Nenhum | Garante teto corporativo |
| CT08 | RF03 | Cliente Cortesia, frete zero | Atraso de 30h | Sem crédito e notificação emitida | Integração | Mock | O serviço de notificação precisa ser simulado para validar o aviso |
| CT09 | RF04 | Cliente novo do próximo trimestre | Atrasio de 30h | Regras existentes não alteradas e o novo tipo usa política própria | Unidade | Stub | O comportamento da política nova deve ser isolado sem mexer nas regras atuais |
| CT10 | RF05 | Veículo parado a 150 m do endereço por 12 min | Ausência do destinatário | Nenhum crédito gerado | Integração | Spy | A telemetria precisa ser consultada para confirmar ausência |
| CT11 | RF06 | Crédito liberado | Emissão de nota | Nota com número sequencial e único | Integração | Spy | Verifica a integração com o Faturamento e a numeração única |
| CT12 | RF07 | Cliente com canal preferido = WhatsApp | Entrega atrasada | Notificação enviada por WhatsApp | Integração | Mock | O canal do cliente precisa ser adaptado ao contrato da API do parceiro |
| CT13 | RF08 | Falha de envio de notificação | Primeira e segunda tentativa com erro | 3 tentativas realizadas e falha final salva em log/auditoria | Integração | Mock | Simula falha e observa o número de retentativas |
| CT14 | RF09 | Mesma confirmação recebida duas vezes | Delayed retry ou duplicata | Somente um crédito gerado | Unidade | Spy | Valida a idempotência da chave de processamento |
| CT15 | RF10 | Portal do cliente | Atualização em tempo real | Posicionamento, previsão e saldo de crédito são exibidos ao vivo | Ponta a ponta | Nenhum | O sistema precisa ser validado em fluxo real de interface |
| CT16 | RNF02 | Garantia liberada | Confirmação de entrega | Crédito emitido em até 5 min | Integração | Spy | Mede o tempo de processamento da cadeia de crédito |

## Mutante que o plano detecta

| Mutante | Caso que o detecta | Por quê |
|---|---|---|
| Alterar a regra do Varejo de 10% para 20% em atrasos de 2h a 24h | CT02 | O caso verifica exatamente o valor de R$ 30,00 para um atraso de 2h01, revelando o erro no percentual. |
| Alterar a condição de ausência comprovada de "até 200 m" para "até 500 m" | CT10 | O caso usa 150 m e 12 min para garantir que a ausência somente seja validada fora do limite. |
| Remover a deduplicação da confirmação de entrega | CT14 | O caso exige que a mesma confirmação emitida duas vezes gere só um crédito, o que falharia sem a chave de idempotência. |
