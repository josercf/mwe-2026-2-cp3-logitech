# 4. Tela do Portal do Cliente (RF10)

A tela de acompanhamento é uma **função do estado**: `tela = f(estado)`. O navegador não
decide regra de negócio. Ele recebe os dados dos serviços indicados na arquitetura
([`02-arquitetura.md`](02-arquitetura.md)), uma função pura `derivarEstado(dados)` escolhe
**um** estado, e cada estado define quais componentes aparecem. Assim, cada estado pode ser
testado sem navegador, só chamando `derivarEstado`.

## Estados da tela

Os estados seguem os status do domínio: `Garantia` (`Ativa → Cumprida | Violada | Isenta`) e
a Confirmação de Entrega. Eles são avaliados **na ordem da tabela**: o primeiro que se aplica é
o estado da tela.

| Estado | Dados disponíveis | O que a tela exibe |
|---|---|---|
| **Carregando** | Nenhum (aguardando a primeira resposta do Pedidos, do Frete e da Garantia) | Esqueleto do mapa, da previsão e do saldo, sem números falsos |
| **Erro ao carregar** | Mensagem de erro da consulta ao pedido | Aviso "Não foi possível carregar o pedido" e o botão **Tentar novamente**; nenhum dado antigo exibido como atual |
| **Em trânsito, no prazo** | Posição do veículo, previsão de chegada e Prazo Prometido (Frete); garantia `Ativa` | Mapa com o veículo e o destino, a previsão de chegada e o prazo prometido, com o selo "No prazo" |
| **Em trânsito, previsão de atraso** | Os mesmos dados, com previsão de chegada **depois** do Prazo Prometido | Os mesmos dados do estado anterior, mais o banner "Previsão de atraso de X h"; para Varejo e Corporativo, o aviso de que o atraso pode gerar crédito; para Cortesia, só o aviso de atraso, sem falar em crédito (RF03) |
| **Posição desatualizada** | Última posição recebida há mais de 90 s (3 pacotes UDP de telemetria perdidos, RNF01) | Última posição no mapa em cor esmaecida e o aviso "Atualizado há X min"; a previsão continua visível com a marcação "estimativa" |
| **Conexão ao vivo perdida** | Os últimos dados recebidos; um dos canais SSE (Frete ou Garantia) caído | Os dados daquele canal congelados e o indicador "Reconectando…"; ao reconectar, a tela recarrega os dados daquele serviço e volta ao estado correto |
| **Entregue no prazo** | Confirmação de Entrega com data e hora; garantia `Cumprida` | Selo "Entregue em DD/MM às HH:MM, dentro do prazo"; o mapa sai da tela |
| **Entregue com atraso, garantia em processamento** | Confirmação de Entrega recebida pela Garantia; atraso calculado; nota ainda não emitida | "Entregue com atraso de X h" e "Estamos processando sua garantia" (pode levar até 5 min, RNF02); nenhum valor de crédito é exibido antes da decisão da Garantia |
| **Entregue com atraso, crédito concedido** | Garantia `Violada`, valor do crédito e número da Nota de Crédito | "Crédito de R$ Y concedido, nota nº N"; o saldo de créditos é atualizado na mesma hora |
| **Entregue com atraso, sem crédito** | Garantia `Violada` com crédito de R$ 0,00 (atraso ≤ 2 h ou cliente Cortesia) | "Entregue com atraso de X h" e o motivo: "Atraso dentro da tolerância de 2 h" ou "Plano Cortesia não inclui crédito" |
| **Garantia isenta, ausência comprovada** | Registro de Ausência; garantia `Isenta` (RF05) | "Tentativa de entrega em DD/MM às HH:MM: destinatário ausente" e "Não há crédito para esta entrega" |

O **saldo de créditos** é um painel independente, com estados próprios, porque vem de uma
consulta separada à Garantia de Prazo e pode falhar sem derrubar o resto da tela:

| Estado do saldo | O que exibe |
|---|---|
| Carregando | Esqueleto do valor |
| Sem saldo | "R$ 0,00", sem destaque |
| Com saldo | O valor do saldo, em destaque |
| Indisponível | "Saldo indisponível no momento"; o restante da tela continua funcionando |

## Árvore de componentes

```
<AcompanhamentoPedido pedidoId>
  <IndicadorConexao statusFrete statusGarantia ultimaAtualizacao />
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
| `AcompanhamentoPedido` | `pedidoId` | Busca os dados no Pedidos, no Frete e na Garantia, assina os dois canais SSE, chama `derivarEstado` e escolhe quais filhos renderizar. É o único componente com estado |
| `IndicadorConexao` | `statusFrete`, `statusGarantia` (`ao-vivo` \| `reconectando`), `ultimaAtualizacao` | Mostra se cada canal ao vivo está ativo e há quanto tempo chegou a última atualização |
| `CabecalhoPedido` | `pedidoId`, `prazoPrometido`, `estado` | Exibe o número do pedido, o prazo prometido e o selo do estado ("No prazo", "Atrasado", "Entregue") |
| `EsqueletoCarregando` | nenhuma | Placeholder visual enquanto os dados não chegam |
| `EstadoErro` | `mensagem`, `onTentarNovamente` | Explica a falha e permite tentar de novo |
| `BannerAtraso` | `atrasoPrevistoMin`, `tipoCliente` | Avisa a previsão de atraso; só menciona crédito se o tipo de cliente tiver crédito |
| `PainelRastreamento` | filhos | Agrupa mapa e previsão enquanto o pedido está em trânsito |
| `MapaVeiculo` | `posicao`, `destino`, `desatualizada` | Desenha o veículo e o endereço; esmaece o veículo quando a posição está desatualizada |
| `PrevisaoChegada` | `previsao`, `prazoPrometido`, `estimativa` | Mostra a previsão de chegada e compara com o prazo prometido |
| `ResumoEntrega` | `confirmadaEm`, `atrasoMin` | Mostra quando a entrega foi confirmada e de quanto foi o atraso, em horas |
| `CartaoGarantia` | `statusGarantia`, `credito`, `numeroNota`, `motivo` | Mostra o resultado da garantia: em processamento, crédito concedido (com nota), sem crédito (com motivo) ou isenta |
| `SaldoCreditos` | `estado`, `saldo` | Mostra o saldo de créditos do cliente, com seus quatro estados próprios |

Só `AcompanhamentoPedido` guarda estado; os outros componentes recebem tudo por props e
não têm lógica de negócio. Por isso cada um pode ser testado isoladamente, passando props
de cada estado.

## Origem dos dados

Os serviços e protocolos são os da tabela de comunicações da arquitetura: **HTTP/REST** para
a carga inicial e **SSE sobre HTTP** para a atualização ao vivo.

| Dado | Serviço de origem | Carga inicial (HTTP/REST) | Atualização ao vivo (SSE) |
|---|---|---|---|
| Número do pedido e endereço de entrega | Pedidos (:8080) | `GET /pedidos/{id}` | Não muda durante o acompanhamento |
| Posição do veículo | Frete (:8000), a partir das posições gravadas pelo Coletor | `GET /pedidos/{id}/rastreamento` | Evento `posicao-atualizada` a cada 30 s; pode haver perda (RNF01), então a tela tolera lacunas e marca a posição como desatualizada após 90 s |
| Previsão de chegada e Prazo Prometido | Frete (:8000) | Mesma resposta | Junto com cada `posicao-atualizada` |
| Tipo de Cliente | Frete (:8000) | Mesma resposta | Não muda; define se o `BannerAtraso` menciona crédito |
| Confirmação de Entrega, Registro de Ausência e status da garantia | Garantia de Prazo | `GET /pedidos/{id}/garantia` | Eventos `garantia-em-processamento`, `garantia-cumprida`, `garantia-violada` (com o valor do crédito, que pode ser R$ 0,00, e o número da nota) e `garantia-isenta` |
| Saldo de créditos | Garantia de Prazo | `GET /clientes/{id}/saldo-creditos` | Evento `saldo-atualizado`, publicado quando um crédito é lançado |

**Como a atualização ao vivo chega ao navegador:**

1. A tela faz a carga inicial por **HTTP/REST** no Pedidos, no Frete e na Garantia de Prazo.
2. Em seguida, abre **dois canais Server-Sent Events (SSE)**, como na arquitetura: um com o
   **Frete**, para posição e previsão, e outro com a **Garantia de Prazo**, para o status da
   garantia e o saldo. SSE atende o RF10 porque o fluxo é só servidor → navegador: o cliente
   não envia nada pela tela. O SSE roda sobre HTTP comum e já reconecta sozinho
   (`EventSource`).
3. Ao reconectar, o navegador envia o `Last-Event-ID` e, por segurança, refaz a carga inicial
   daquele serviço. Isso cobre eventos perdidos enquanto a conexão estava caída.
4. Cada canal só entrega eventos dos pedidos do cliente autenticado.

Esse fluxo é verificado pelo caso **CT30** do plano de testes (RF10). Os estados da tela podem
ganhar testes de unidade da função `derivarEstado`, um por linha da tabela de estados.
