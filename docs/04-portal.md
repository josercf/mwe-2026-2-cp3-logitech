# 4. Tela do Portal do Cliente (RF10)

## Estados da tela

A tela é uma função do estado da entrega e do cliente. A experiência principal é um painel de rastreio com mapa, previsão, status de entrega e saldo de créditos.

| Estado | Dados disponíveis | O que a tela exibe |
|---|---|---|
| Pedido em trânsito | posição do veículo, rota, previsão de chegada, tempo restante, status de entrega | Mapa com veículo em movimento, linha de rota, ETA e badge “Em trânsito” |
| Entrega próxima | distância até o destino, previsão ajustada, veículo em baixa velocidade ou parado próximo ao endereço | Destaque visual de chegada iminente, tempo restante e indicação de que a entrega está próxima |
| Entrega em atraso | atraso em horas, valor de crédito estimado, motivo do atraso, histórico | Alerta de atraso com valor de crédito e atualização do saldo disponível |
| Entrega concluída | confirmação de entrega, crédito emitido, saldo atualizado | Mensagem de conclusão, confirmação do recebimento e novo saldo de créditos |
| Ausência do destinatário comprovada | telemetria invalidando crédito, posição do veículo, observação do motivo | Alerta de ausência comprovada e ausência de crédito, sem bloqueio do rastreio |

## Árvore de componentes

```tsx
<AcompanhamentoPedido>
  <HeaderPedido />
  <ResumoEntrega />
  <MapaEntrega />
  <PainelInformacoes />
  <ListaEventos />
  <SaldoCreditos />
</AcompanhamentoPedido>
```

| Componente | Props recebidas | Responsabilidade |
|---|---|---|
| AcompanhamentoPedido | pedidoId, clienteId, canalAtualizacao | Agrupa os dados do pedido e controla o ciclo de atualização ao vivo. |
| HeaderPedido | numeroPedido, status, dataPrevista | Exibe identidade do pedido e o status geral da entrega. |
| ResumoEntrega | endereco, prazoPrometido, previsaoChegada, atrasoHoras | Mostra resumo executivo da entrega e do atraso atual. |
| MapaEntrega | posicaoVeiculo, rota, enderecoDestino | Renderiza mapa com a posição do veículo e o destino final. |
| PainelInformacoes | distancia, velocidade, tempoRestante, valorCredito | Exibe informações operacionais e financeiras em painel compacto. |
| ListaEventos | eventosEntrega[] | Mostra histórico da entrega, como “Saiu da origem”, “Próximo do destino”, “Entrega confirmada”. |
| SaldoCreditos | saldoAtual, historicoCreditos | Apresenta o saldo de créditos do cliente e o valor do último crédito gerado. |

## Origem dos dados

Cada dado da interface tem origem em um serviço diferente, mas todos convergem para o portal em tempo real.

- Posição do veículo e rota: vêm da Telemetria Veicular, publicada por eventos e consumida pelo portal via SSE.
- Previsão de chegada: calculada pelo serviço de Frete e atualizada pela Garantia de Prazo quando há atraso ou mudança de rota.
- Atraso em horas: medido no contexto de Frete e Prazo e reenviado para o portal ao atualizar o status da entrega.
- Saldo de créditos: calculado pela Garantia de Prazo e persistido no domínio de cliente/portal, atualizado assim que a nota de crédito é emitida.
- Confirmação de entrega: registrada no fluxo principal de frete e consumida pela Garantia de Prazo para decidir se haverá crédito.

A atualização ao vivo chega ao navegador por Server-Sent Events (SSE), em um canal de eventos específico para o pedido. A página mantém uma conexão aberta com o backend do portal e recebe mensagens quando há mudança na posição, no status da entrega ou no saldo de crédito. Isso permite que a interface seja atualizada sem polling constante e sem recarga manual.
