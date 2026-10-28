# 3. Plano de testes

Os casos seguem a modelagem ([`01-dominio.md`](01-dominio.md)) e a arquitetura
([`02-arquitetura.md`](02-arquitetura.md)): a Garantia consome a confirmação da fila durável,
consulta o Frete, valida a ausência, solicita a nota ao Faturamento e publica a solicitação de
notificação.

## Pirâmide de testes

| Nível | Quantidade de casos | O que cobre |
|---|---|---|
| Unidade | 31 (≈ 82%) | Política de Compensação (faixas, multiplicador, teto, arredondamento), Factory/registro de políticas (RF04), cálculo e arredondamento do atraso, `ValidacaoAusencia` (geocerca e janela), regras do agregado `Garantia` (cortesia, isenção, gatilho único de aviso), saldo de créditos, recepção de telemetria com perda, escolha de canal pelo Adapter e retentativas pelo Decorator |
| Integração | 4 (≈ 11%) | Idempotência da confirmação com banco real (RF09), idempotência e numeração concorrente de notas no Faturamento (RF06, RNF03) e durabilidade da confirmação no RabbitMQ (RNF01) |
| Ponta a ponta | 3 (≈ 8%) | Fluxo completo da confirmação até a nota emitida (RNF02), Portal ao vivo por SSE (RF10) e subida do ambiente com um comando (RNF04) |

**Por que essa proporção:** o maior risco da Garantia de Prazo está nas regras de cálculo,
que têm muitos valores-limite (3 faixas × 2 limites × 3 tipos de cliente × teto, mais o
arredondamento do atraso e os limites da geocerca). Essas regras são funções puras: rodam em
milissegundos e não dependem de infraestrutura, então ficam na base da pirâmide. As chamadas
REST ao Frete e ao Faturamento e a publicação na fila são substituídas por dublês na unidade,
porque o que se verifica ali é a regra da Garantia. A integração aparece só onde um dublê
**esconderia** o defeito: concorrência, constraint de unicidade e reentrega do RabbitMQ só se
comportam de verdade com banco e broker reais. Os testes ponta a ponta são poucos porque são
lentos e frágeis. Eles validam o que só existe com o sistema inteiro rodando: o tempo de 5 min,
a atualização ao vivo e o `docker compose up`.

## Decisões sobre ambiguidades dos requisitos

| Ponto ambíguo | Requisito | Decisão adotada no plano |
|---|---|---|
| "Atraso medido em horas", mas os limites "até 2 h" e "acima de 2 h" exigem precisão, e os horários têm segundos | RF01, RF02 | O atraso é contado em **minutos, arredondados para cima**: qualquer fração de minuto conta como minuto inteiro. 2h00m00s = 120 min (sem crédito); 2h00m01s = 121 min (primeiro valor "acima de 2 h"). Isso equivale a comparar em segundos, sem perder o valor-limite |
| Os limites de faixa são inclusivos? | RF02 | "Até X h" é **inclusivo** e "acima de X h" é **exclusivo**: 24h00 → 10%, 24h01 → 25%; 72h00 → 25%, 72h01 → 50% |
| Entrega antes do prazo gera atraso negativo | RF01 | Atraso ≤ 0 é tratado como **0** (entrega no prazo, sem crédito) |
| O teto vale antes ou depois de dobrar o percentual? | RF03 | O teto é aplicado **depois** do multiplicador: Corporativo acima de 72 h = 100% do frete, limitado a R$ 2.000 |
| O requisito não define o arredondamento do crédito | RF02 | Valores em centavos, com arredondamento **HALF_UP** para 2 casas |
| "Cortesia (frete zero)": é um tipo de cliente ou qualquer pedido com frete zero? | RF03 | **Cortesia é um tipo de cliente**, informado pelo Frete na resposta à Garantia |
| A arquitetura não diz de onde vem o Tipo de Cliente | RF02, RF03 | A consulta da Garantia ao Frete devolve `prazoPrometido`, `valorFrete` e `tipoCliente`, porque o Frete precifica pelo tipo de cliente |
| A partir de quanto atraso o Cortesia é notificado? | RF03 | **Qualquer atraso maior que 0**. A tolerância de 2 h vale só para o crédito; o RF03 fala em notificar "do atraso", sem carência |
| Qual mensagem dispara o aviso ao cliente? | RF07 | Só a `NotificacaoSolicitada` publicada pela Garantia, depois que o Faturamento devolve o número da nota. O Faturamento não envia aviso de crédito, para o cliente não ser notificado duas vezes |
| A Garantia pode repetir a solicitação de nota (timeout na chamada REST) | RF06, RF09 | O Faturamento é idempotente pelo `creditoId`: a mesma solicitação devolve a mesma nota, sem consumir outro número |
| "Retentada até 3 vezes" | RF08 | **1 envio original + 3 retentativas = 4 tentativas** no máximo |
| "A até 200 m" e "pelo menos 10 min" são inclusivos? | RF05 | Os dois são **inclusivos**: 200 m e 10min00 comprovam a ausência; 201 m ou 9min59 não comprovam |
| "Sequencial e nunca repetido": pode haver lacunas? | RF06, RNF03 | O plano verifica que os números são **únicos e crescentes**. Lacunas (por exemplo, após um rollback) não são verificadas, porque o requisito não as proíbe |

## Casos de teste

| ID | Requisito | Pré-condição | Entrada | Resultado esperado | Nível | Dublê | Justificativa do dublê |
|---|---|---|---|---|---|---|---|
| CT01 | RF02 | Cliente Varejo, frete de R$ 300,00 | Atraso de 2h00 (120 min) | Crédito de R$ 0,00 | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT02 | RF02 | Cliente Varejo, frete de R$ 300,00 | Atraso de 2h01 (121 min) | Crédito de R$ 30,00 (10%) | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT03 | RF02 | Cliente Varejo, frete de R$ 300,00 | Atraso de 24h00 (1.440 min) | Crédito de R$ 30,00 (10%) | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT04 | RF02 | Cliente Varejo, frete de R$ 300,00 | Atraso de 24h01 (1.441 min) | Crédito de R$ 75,00 (25%) | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT05 | RF02 | Cliente Varejo, frete de R$ 300,00 | Atraso de 72h00 (4.320 min) | Crédito de R$ 75,00 (25%) | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT06 | RF02 | Cliente Varejo, frete de R$ 300,00 | Atraso de 72h01 (4.321 min) | Crédito de R$ 150,00 (50%) | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT07 | RF02 | Cliente Varejo, frete de R$ 1.000,00 | Atraso de 72h01 | Crédito de R$ 500,00 (exatamente no teto) | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT08 | RF02 | Cliente Varejo, frete de R$ 1.000,02 | Atraso de 72h01 | Crédito de R$ 500,00 (50% = R$ 500,01, limitado ao teto) | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT09 | RF03 | Cliente Corporativo, frete de R$ 300,00 | Atraso de 2h01 | Crédito de R$ 60,00 (20%) | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT10 | RF03 | Cliente Corporativo, frete de R$ 300,00 | Atraso de 24h01 | Crédito de R$ 150,00 (50%) | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT11 | RF03 | Cliente Corporativo, frete de R$ 300,00 | Atraso de 72h01 | Crédito de R$ 300,00 (100%) | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT12 | RF03 | Cliente Corporativo, frete de R$ 2.000,00 | Atraso de 72h01 | Crédito de R$ 2.000,00 (exatamente no teto) | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT13 | RF03 | Cliente Corporativo, frete de R$ 2.000,02 | Atraso de 72h01 | Crédito de R$ 2.000,00 (100% = R$ 2.000,02, limitado ao teto) | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT14 | RF02 | Cliente Varejo, frete de R$ 33,35 | Atraso de 2h01 | Crédito de R$ 3,34 (10% = 3,335, arredondado HALF_UP) | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT15 | RF01 | Prazo Prometido 27/10 10:00 | Confirmação de entrega 27/10 09:00 | Atraso = 0; garantia `Cumprida`; crédito de R$ 0,00 | Unidade | Nenhum | Cálculo puro entre duas datas |
| CT16 | RF01 | Frete responde à consulta com Prazo Prometido 27/10 10:00, frete de R$ 300,00 e cliente Varejo | `EntregaConfirmada` com confirmação 27/10 12:01 | Atraso de 121 min; crédito de R$ 30,00 | Unidade | Stub | O cliente REST do Frete só fornece dados; o caso verifica o cálculo, não a chamada |
| CT17 | RF03 | Cliente Cortesia, frete de R$ 0,00 | Atraso de 30h | Crédito de R$ 0,00; garantia `Violada`; nenhuma nota solicitada; `NotificacaoSolicitada` de atraso publicada exatamente 1 vez | Unidade | Spy | O spy registra as mensagens publicadas na fila para conferir, depois da execução, que o aviso de atraso saiu mesmo sem crédito |
| CT18 | RF04 | Um tipo de cliente fictício "Parceiro" (3×, teto de R$ 1.000) é registrado na fábrica de políticas dentro do teste | Pedido "Parceiro", frete de R$ 300,00, atraso de 24h01 | A fábrica devolve a política nova, que calcula R$ 225,00; o Varejo, obtido da mesma fábrica, continua devolvendo R$ 75,00. A ausência de alteração nas classes existentes é garantida pelo design (uma estratégia por tipo, entrando por registro) e verificada pelos casos CT01 a CT17, que continuam passando | Unidade | Nenhum | Verifica a extensão por registro de uma estratégia nova, sem dependência externa |
| CT19 | RF05 | Endereço de entrega conhecido; registro de ausência às 14:00 | Posições do veículo parado a 200 m do endereço das 13:50 às 14:00 (10min00) | `ValidacaoAusencia` retorna ausência comprovada | Unidade | Nenhum | Avaliação pura sobre uma lista de posições |
| CT20 | RF05 | Endereço de entrega conhecido; registro de ausência às 14:00 | Posições do veículo parado a 201 m das 13:50 às 14:00 | `ValidacaoAusencia` retorna ausência **não** comprovada | Unidade | Nenhum | Avaliação pura sobre uma lista de posições |
| CT21 | RF05 | Endereço de entrega conhecido; registro de ausência às 14:00:00 | Posições do veículo parado a 150 m das 13:50:01 às 14:00:00 (9min59) | `ValidacaoAusencia` retorna ausência **não** comprovada | Unidade | Nenhum | Avaliação pura sobre uma lista de posições |
| CT22 | RF05 | Garantia ativa, Varejo, frete de R$ 300,00; registro de ausência gravado; posições gravadas comprovam a ausência (como no CT19) | `EntregaConfirmada` com atraso de 30h | Garantia `Isenta`; o Faturamento não é chamado | Unidade | Mock | O mock do cliente REST do Faturamento verifica a interação: nenhuma nota pode ser solicitada. As posições vêm de um stub auxiliar, que só fornece dados |
| CT23 | RF07 | Cliente com canal preferido WhatsApp, guardado nas Notificações | `NotificacaoSolicitada` de crédito de R$ 75,00, nota nº 1234 | API do parceiro chamada 1 vez com o payload no formato do parceiro; provedor de e-mail não chamado | Unidade | Mock | Verifica a interação e a tradução feita pelo Adapter sem depender da API externa |
| CT24 | RF08 | Canal falha nas 2 primeiras tentativas e responde com sucesso na 3ª | Envio de notificação pelo Decorator de retentativa | Notificação `Enviada`; exatamente 3 chamadas ao canal; nada na fila de falhas | Unidade | Mock | O caso verifica o número de chamadas, que é uma interação |
| CT25 | RF08 | Canal falha em todas as tentativas | Envio de notificação pelo Decorator de retentativa | Exatamente 4 chamadas (1 + 3 retentativas); status `FalhaDefinitiva`; 1 mensagem na fila de falhas (DLQ) | Unidade | Spy | O spy registra o que chegou à DLQ para provar que a falha não foi descartada; as falhas do canal são programadas por um stub auxiliar, que só fornece respostas |
| CT26 | RF09 | Garantia ativa, Varejo, frete de R$ 300,00; PostgreSQL real (Testcontainers) | A mesma `EntregaConfirmada` (mesmo `entregaId`, atraso de 30h) consumida 2 vezes | Exatamente 1 crédito de R$ 75,00 gravado e 1 solicitação de nota | Integração | Nenhum | A garantia vem da restrição `UNIQUE` do banco real usada pelo Repository; um dublê esconderia exatamente esse comportamento |
| CT27 | RF06, RNF03 | Faturamento com PostgreSQL real (Testcontainers) | 1.000 solicitações de nota concorrentes, com `creditoId` diferentes | 1.000 notas com números distintos e crescentes | Integração | Nenhum | Condição de corrida só aparece com banco e transações reais |
| CT28 | RNF01 | Coletor e RabbitMQ reais; consumidor da Garantia é derrubado antes do ack | Confirmação de entrega enviada ao Coletor por TCP, com atraso de 30h | A mensagem fica na fila durável e é reentregue após o consumidor voltar; exatamente 1 crédito gerado | Integração | Nenhum | Verifica a durabilidade do broker, que não existe num dublê |
| CT29 | RNF02 | Ambiente completo no ar; Varejo, frete de R$ 300,00 | Confirmação de entrega enviada ao Coletor com 30h de atraso | Nota de crédito de R$ 75,00 emitida em até 5 min após a confirmação | Ponta a ponta | Nenhum | Mede o tempo real do fluxo entre os serviços |
| CT30 | RF10 | Ambiente completo no ar; cliente com o Portal aberto | Nova posição do veículo gravada; depois, crédito concedido | Mapa e previsão de chegada atualizados pelo SSE do Frete, e saldo atualizado pelo SSE da Garantia, sem recarregar a página | Ponta a ponta | Nenhum | Verifica a atualização ao vivo de ponta a ponta no navegador |
| CT31 | RNF04 | Repositório recém-clonado | `docker compose up` | Todos os serviços em estado `healthy` | Ponta a ponta | Nenhum | Verifica a subida real dos contêineres |
| CT32 | RF01, RF02 | Prazo Prometido 27/10 10:00:00; Varejo, frete de R$ 300,00 | Confirmação de entrega 27/10 12:00:01 (2h00m01s) | Atraso de 121 min (arredondado para cima); crédito de R$ 30,00 | Unidade | Nenhum | Cálculo puro entre duas datas |
| CT33 | RF05 | Garantia ativa, Varejo, frete de R$ 300,00; registro de ausência gravado; posições gravadas a 201 m (como no CT20) | `EntregaConfirmada` com atraso de 30h | Garantia `Violada`; nota de R$ 75,00 solicitada ao Faturamento exatamente 1 vez | Unidade | Mock | O mock do cliente REST do Faturamento verifica que a solicitação saiu uma vez e com o valor certo |
| CT34 | RF06, RF09 | Faturamento com PostgreSQL real (Testcontainers) | A mesma solicitação de nota (mesmo `creditoId`) enviada 2 vezes | 1 nota emitida; as duas respostas trazem o mesmo número | Integração | Nenhum | A idempotência depende da restrição `UNIQUE` em `creditoId` no banco real |
| CT35 | RF07 | Varejo, atraso de 30h; o Faturamento responde com a nota nº 1234 | `EntregaConfirmada` | Exatamente 1 `NotificacaoSolicitada` publicada, com o crédito de R$ 75,00 e a nota nº 1234 | Unidade | Spy | O spy registra as mensagens publicadas para conferir quantidade e conteúdo depois da execução; a resposta do Faturamento vem de um stub auxiliar |
| CT36 | RF03 | Cliente Cortesia, frete de R$ 0,00 | Atraso de 1 min | Crédito de R$ 0,00; `NotificacaoSolicitada` de atraso publicada exatamente 1 vez | Unidade | Spy | O spy confirma que o aviso de atraso sai mesmo dentro da tolerância de 2 h, que vale só para o crédito |
| CT37 | RNF01 | Coletor recebendo posições de um veículo | Pacotes UDP das 14:00:00, 14:00:30 e 14:01:30 (o de 14:01:00 se perdeu) | As 3 posições recebidas são gravadas; nenhum erro, nenhuma retransmissão solicitada | Unidade | Nenhum | O caso verifica só o tratamento dos pacotes recebidos, sem dependência externa |
| CT38 | RF10 | Saldo do cliente de R$ 30,00 | O mesmo crédito de R$ 75,00 (mesmo `creditoId`) lançado 2 vezes | Saldo de R$ 105,00 | Unidade | Nenhum | Regra pura do agregado `SaldoCreditos` |

## Mutante que o plano detecta

| Mutante | Caso que o detecta | Por quê |
|---|---|---|
| Na primeira faixa, `atraso > 120` trocado por `atraso >= 120` | CT01 | Com 2h00, o mutante passa a dar R$ 30,00 em vez de R$ 0,00 |
| Na segunda faixa, `atraso > 1440` trocado por `atraso >= 1440` | CT03 | Com 24h00, o mutante passa a dar 25% (R$ 75,00) em vez de 10% (R$ 30,00) |
| Arredondamento do atraso para cima trocado por truncamento | CT32 | Com 2h00m01s, o atraso passaria a 120 min e o crédito a R$ 0,00 em vez de R$ 30,00 |
| Teto aplicado **antes** do multiplicador (ou teto do Varejo usado no Corporativo) | CT12, CT13 | O Corporativo com frete de R$ 2.000,00 retornaria R$ 1.000,00 (ou R$ 500,00) em vez de R$ 2.000,00 |
| `min(credito, teto)` trocado por `max(credito, teto)` | CT01, CT07 | Com atraso de 2h00, o crédito passaria a ser R$ 500,00 em vez de R$ 0,00 |
| Na geocerca, `distancia <= 200` trocado por `distancia < 200` | CT19 | A 200 m exatos, a ausência deixaria de ser comprovada |
| Chamada à `ValidacaoAusencia` removida da Garantia | CT22 | A nota seria solicitada ao Faturamento mesmo com a ausência comprovada |
| Garantia publicando a notificação antes **e** depois da resposta do Faturamento | CT35 | Seriam publicadas 2 `NotificacaoSolicitada` em vez de 1 |
| Remoção da verificação de `creditoId` no Faturamento | CT34 | A segunda solicitação geraria uma segunda nota, com outro número |
| No laço de retentativas, `tentativas <= 3` trocado por `tentativas < 3` | CT25 | O canal seria chamado 3 vezes em vez de 4 |
| Remoção da verificação de `entregaId` já processado | CT26 | A segunda entrega duplicada geraria um segundo crédito |
