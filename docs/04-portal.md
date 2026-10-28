# 4. Tela do Portal do Cliente (RF10)

A tela de acompanhamento é uma **função do estado**: `tela = f(estado)`. O navegador não
decide regra de negócio. Ele recebe os dados do BFF, uma função pura `derivarEstado(dados)`
escolhe **um** estado, e cada estado define quais componentes aparecem. Assim, cada estado
pode ser testado sem navegador, só chamando `derivarEstado`.

## Estados da tela

Os estados seguem os status do domínio: `Garantia` (`Ativa → Cumprida | Violada | Isenta`) e
a Confirmação de Entrega. Eles são avaliados **na ordem da tabela**: o primeiro que se aplica é
o estado da tela.

| Estado | Dados disponíveis | O que a tela exibe |
|---|---|---|
| **Carregando** | Nenhum (aguardando a primeira resposta do BFF) | Esqueleto do mapa, da previsão e do saldo, sem números falsos |
| **Erro ao carregar** | Mensagem de erro do BFF | Aviso "Não foi possível carregar o pedido" e o botão **Tentar novamente**; nenhum dado antigo exibido como atual |
| **Em trânsito, no prazo** | Posição do veículo, previsão de chegada, Prazo Prometido; garantia `Ativa` | Mapa com o veículo e o destino, a previsão de chegada e o prazo prometido, com o selo "No prazo" |
| **Em trânsito, previsão de atraso** | Os mesmos dados, com previsão de chegada **depois** do Prazo Prometido | Os mesmos dados do estado anterior, mais o banner "Previsão de atraso de X h"; para Varejo e Corporativo, o aviso de que o atraso pode gerar crédito; para Cortesia, só o aviso de atraso, sem falar em crédito (RF03) |
| **Posição desatualizada** | Última posição recebida há mais de 90 s (3 pacotes de telemetria perdidos, RNF01a) | Última posição no mapa em cor esmaecida e o aviso "Atualizado há X min"; a previsão continua visível com a marcação "estimativa" |
| **Conexão ao vivo perdida** | Os últimos dados recebidos; canal ao vivo caído | Os dados congelados e o indicador "Reconectando…"; ao reconectar, a tela recarrega o snapshot e volta ao estado correto |
| **Entregue no prazo** | Confirmação de Entrega com data e hora; garantia `Cumprida` | Selo "Entregue em DD/MM às HH:MM, dentro do prazo"; o mapa sai da tela |
| **Entregue com atraso, verificando a garantia** | Confirmação de Entrega e atraso; garantia `Ativa` aguardando o veredito de um Registro de Ausência anterior (RF05) | "Entregue com atraso de X h" e "Estamos verificando a garantia desta entrega"; nenhum valor de crédito é exibido antes do veredito |
| **Entregue com atraso, crédito em processamento** | Confirmação de Entrega, atraso calculado; garantia `Violada`; nota de crédito ainda não emitida | "Entregue com atraso de X h" e "Crédito de R$ Y em processamento" (pode levar até 5 min, RNF02) |
| **Entregue com atraso, crédito concedido** | Os mesmos dados, mais o número da Nota de Crédito e o valor | "Crédito de R$ Y concedido, nota nº N"; o saldo de créditos é atualizado na mesma hora |
| **Entregue com atraso, sem crédito** | Confirmação de Entrega e atraso; política retornou R$ 0,00 (atraso ≤ 2 h ou cliente Cortesia) | "Entregue com atraso de X h" e o motivo: "Atraso dentro da tolerância de 2 h" ou "Plano Cortesia não inclui crédito" |
| **Garantia isenta, ausência comprovada** | Registro de Ausência; garantia `Isenta` (RF05) | "Tentativa de entrega em DD/MM às HH:MM: destinatário ausente" e "Não há crédito para esta entrega" |

O **saldo de créditos** é um painel independente, com estados próprios, porque vem de outro
contexto (Faturamento) e pode falhar sem derrubar o resto da tela:

| Estado do saldo | O que exibe |
|---|---|
| Carregando | Esqueleto do valor |
| Sem saldo | "R$ 0,00", sem destaque |
| Com saldo | O valor do saldo, em destaque |
| Indisponível | "Saldo indisponível no momento"; o restante da tela continua funcionando |

## Árvore de componentes

```
<AcompanhamentoPedido pedidoId>
  <IndicadorConexao status ultimaAtualizacao />
  <CabecalhoPedido pedidoId prazoPrometido estado />
  <EsqueletoCarregando />                                  // só em Carregando
  <EstadoErro mensagem onTentarNovamente />                // só em Erro ao carregar
  <BannerAtraso atrasoPrevistoMin tipoCliente />           // só em Previsão de atraso
  <PainelRastreamento>                                     // só enquanto em trânsito
    <MapaVeiculo posicao destino desatualizada />
    <PrevisaoChegada previsao prazoPrometido estimativa />
  </PainelRastreamento>
  <ResumoEntrega confirmadaEm atrasoMin />                 // só depois da entrega
  <CartaoGarantia statusGarantia credito numeroNota motivo /> // só depois da entrega
  <SaldoCreditos estado saldo />                           // sempre, com estado próprio
</AcompanhamentoPedido>
```

| Componente | Props recebidas | Responsabilidade |
|---|---|---|
| `AcompanhamentoPedido` | `pedidoId` | Busca o snapshot no BFF, assina o canal ao vivo, chama `derivarEstado` e escolhe quais filhos renderizar. É o único componente com estado |
| `IndicadorConexao` | `status` (`ao-vivo` \| `reconectando`), `ultimaAtualizacao` | Mostra se a tela está recebendo dados ao vivo e há quanto tempo chegou a última atualização |
| `CabecalhoPedido` | `pedidoId`, `prazoPrometido`, `estado` | Exibe o número do pedido, o prazo prometido e o selo do estado ("No prazo", "Atrasado", "Entregue") |
| `EsqueletoCarregando` | nenhuma | Placeholder visual enquanto o snapshot não chega |
| `EstadoErro` | `mensagem`, `onTentarNovamente` | Explica a falha e permite tentar de novo |
| `BannerAtraso` | `atrasoPrevistoMin`, `tipoCliente` | Avisa a previsão de atraso; só menciona crédito se o tipo de cliente tiver crédito |
| `PainelRastreamento` | filhos | Agrupa mapa e previsão enquanto o pedido está em trânsito |
| `MapaVeiculo` | `posicao`, `destino`, `desatualizada` | Desenha o veículo e o endereço; esmaece o veículo quando a posição está desatualizada |
| `PrevisaoChegada` | `previsao`, `prazoPrometido`, `estimativa` | Mostra a previsão de chegada e compara com o prazo prometido |
| `ResumoEntrega` | `confirmadaEm`, `atrasoMin` | Mostra quando a entrega foi confirmada e de quanto foi o atraso, em horas |
| `CartaoGarantia` | `statusGarantia`, `credito`, `numeroNota`, `motivo` | Mostra o resultado da garantia: verificando (aguardando o veredito da ausência), crédito em processamento, concedido (com nota), sem crédito (com motivo) ou isenta |
| `SaldoCreditos` | `estado`, `saldo` | Mostra o saldo de créditos do cliente, com seus quatro estados próprios |

Só `AcompanhamentoPedido` guarda estado; os outros componentes recebem tudo por props e
não têm lógica de negócio. Por isso cada um pode ser testado isoladamente, passando props
de cada estado.

## Origem dos dados

| Dado | Contexto de origem | Carga inicial | Atualização ao vivo |
|---|---|---|---|
| Posição do veículo | Rastreamento | `GET /pedidos/{id}/acompanhamento` no BFF | Evento `posicao-atualizada` a cada 30 s; pode haver perda (RNF01a), então a tela tolera lacunas e marca a posição como desatualizada após 90 s |
| Previsão de chegada | Rastreamento | Mesmo snapshot | Junto com cada `posicao-atualizada` |
| Prazo Prometido | Frete (evento `FreteContratado`), guardado na Garantia de Prazo | Mesmo snapshot | Não muda depois da contratação |
| Tipo de Cliente | Pedidos e Entrega (evento `PedidoCriado`) | Mesmo snapshot | Não muda depois da criação do pedido; define se o `BannerAtraso` menciona crédito |
| Confirmação de Entrega e Registro de Ausência | Pedidos e Entrega | Mesmo snapshot | Eventos `entrega-confirmada` e `ausencia-registrada` |
| Status da garantia, atraso e valor do crédito | Garantia de Prazo | Mesmo snapshot | Eventos `garantia-cumprida`, `garantia-violada` (com o valor do crédito, que pode ser R$ 0,00), `garantia-isenta` e `garantia-aguardando-veredito` |
| Número da Nota de Crédito e saldo de créditos | Faturamento | `GET /clientes/{id}/saldo-creditos` no BFF | Evento `nota-de-credito-emitida`, que traz o saldo novo |

**Como a atualização ao vivo chega ao navegador:**

1. Os contextos publicam seus eventos no broker, como já descrito na modelagem e na
   arquitetura.
2. O **BFF do Portal** consome esses eventos e mantém um *read model* por cliente. Ele não
   tem regra de negócio, só junta os dados para a tela.
3. O navegador abre **um canal Server-Sent Events (SSE)** com o BFF (`GET /clientes/{id}/eventos`).
   Escolhemos SSE e não WebSocket porque o fluxo é só servidor → navegador: o cliente não
   envia nada pela tela. O SSE roda sobre HTTP comum e já reconecta sozinho
   (`EventSource`).
4. Ao reconectar, o navegador envia o `Last-Event-ID` e, por segurança, recarrega o snapshot
   pelo `GET`. Isso cobre eventos perdidos enquanto a conexão estava caída.
5. O canal só entrega eventos dos pedidos do cliente autenticado.

Esse fluxo é verificado pelo caso **CT30** do plano de testes (RF10). Os estados da tela podem
ganhar testes de unidade da função `derivarEstado`, um por linha da tabela de estados.
