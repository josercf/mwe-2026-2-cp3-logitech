# 5. Uso de assistentes de IA

A dupla usou assistentes de IA durante toda a atividade:

- **Claude (Claude Code)**, como apoio para estruturar os documentos, revisar decisões e
  implementar a regra de cálculo. Os commits feitos por ele estão identificados no histórico
  com a linha `Co-Authored-By: Claude`.
- **Outro assistente de IA**, usado pela dupla para gerar uma revisão crítica da modelagem do
  domínio (7 apontamentos), cujos pontos a dupla decidiu aplicar.
- **Um assistente de IA usado pelo outro integrante na arquitetura** (`02-arquitetura.md` e
  diagrama). O uso nessa entrega não foi registrado em detalhe.

A forma de uso foi iterativa: a dupla pedia uma proposta, questionava e revisava o resultado,
e só então pedia o commit. A tabela está em **ordem cronológica**: decisões das linhas finais
substituem as anteriores quando tratam do mesmo ponto. A versão final de todos os documentos
segue a arquitetura (ver as linhas a partir de "Integração").

| Entrega | O que foi pedido | O que o assistente sugeriu | Decisão da dupla | Motivo |
|---|---|---|---|---|
| Planejamento | Um direcionamento para atender as entregas no tempo da prova | Roteiro por entrega, com as decisões que cada critério de avaliação cobra | **Aceito como roteiro**, com organização própria: trabalho numa branch separada da `main` e divisão da arquitetura com o outro integrante, em outra branch | Não arriscar a `main` durante a atividade e permitir trabalho em paralelo sem conflito de arquivos |
| Modelagem | Um exemplo do `01-dominio.md` preenchido | Sete contextos, mapa de contexto em Mermaid, agregados e linguagem ubíqua | **Aceito só depois de questionar.** A dupla pediu que o assistente explicasse o método usado e desse motivos para *não* adotar a proposta antes de seguir | Entender a modelagem para conseguir defendê-la, em vez de copiá-la |
| Modelagem | Motivos para não adotar a proposta | Pontos fracos: contexto "Entrega" criado à parte, RF05 defensável nos dois lados, `PoliticaCompensacao` como agregado, saldo no Faturamento, excesso de detalhe no mapa | **`PoliticaCompensacao` reclassificada** como serviço de domínio; **RF05 mantido no Rastreamento**; demais pontos mantidos | A política não tem estado nem ciclo de vida, então não é agregado; o RF05 fica onde está a linguagem de GPS, distância e tempo parado |
| Modelagem | Aplicar uma revisão da modelagem que a dupla obteve de **outro assistente de IA**, com 7 apontamentos | Implementação dos ajustes no documento | **A dupla decidiu aplicar todos os apontamentos:** RNF01 dividido em RNF01a e RNF01b; regra do RF05 reescrita no agregado; origem de Tipo de Cliente, Valor do Frete e Canal Preferido (`FreteContratado`, `PedidoCriado`); gatilho único do aviso de crédito; atraso arredondado para cima; ordem entre ausência e confirmação; estado do Cliente Cortesia | Cada requisito com um único dono, como pede o critério, e eliminação de lacunas que afetariam os testes e a arquitetura |
| Modelagem | Conferir o domínio antes de subir | Dois ajustes: tirar `PoliticaCompensacao` da tabela de agregados e definir Cortesia como tipo de cliente | **Aceito** | Coerência com o plano de testes |
| Testes | Plano de testes preenchido, atento às contradições dos requisitos | 31 casos, uma tabela de ambiguidades e uma tabela de mutantes | **Aceito, com a revisão antes do commit** pedida pela dupla | O plano é a base da implementação em TDD, então foi revisado antes de ir para o repositório |
| Testes | (mesma solicitação) | Troca do CT01 de exemplo do template de 1h59 para 2h00 | **Aceito** | Com o atraso em minutos, o limite exato é 2h00 (último valor sem crédito); 1h59 não testa a fronteira |
| Testes | (mesma solicitação) | Interpretações: "3 retentativas" = 4 tentativas; arredondamento HALF_UP; limites de faixa inclusivos; lacunas na numeração não verificadas | **Aceito** | O enunciado não define esses pontos; a dupla preferiu registrar a interpretação a deixá-la implícita |
| Testes | Análise do plano antes do commit | Lacunas: segundos no horário, aviso ao Cortesia com atraso pequeno, falta de caso de e-mail, CT18 frágil, dois dublês no CT25 | **Incorporado** na revisão do domínio: casos CT32 a CT36, CT18 reescrito, CT25 com um único dublê declarado | Os valores-limite precisam ser exatos, e o CT18 não podia prometer o que um teste não consegue provar |
| Tela | Tela do portal coerente com domínio e testes | Estados derivados de uma função pura `derivarEstado`, painel de saldo independente, SSE em vez de WebSocket, estado "posição desatualizada" após 90 s | **Aceito.** A dupla pediu também a correção do mapa de contexto, que não mostrava a Garantia e a Entrega alimentando o Portal | O fluxo de dados é só servidor → navegador; sem a correção, o portal consumiria dados que o domínio não mostrava |
| Tela | Alinhar a tela com o domínio revisado | Novo estado "verificando a garantia", origem do Tipo de Cliente e eventos da garantia | **Aceito** | Consequência direta da espera pelo veredito da ausência (RF05) |
| Implementação | Implementar a regra em TDD seguindo o desenho discutido até ali (Strategy por tipo de cliente) | Python com `unittest`; ciclos `test:` → `feat:` → `refactor:`, com o teste confirmado em vermelho antes de cada código; faixas como dados em vez de uma classe por faixa | **Aceito.** Os commits de TDD foram feitos pelo assistente, por isso estão com poucos segundos de diferença entre si; a ordem teste → código foi verificada em cada ciclo | `unittest` não exige instalação; o registro de políticas atende o RF04 sem alterar as classes existentes |
| Implementação | Como visualizar e rodar a implementação | VS Code local, Codespaces, github.dev e o histórico de commits no GitHub; exercício de mutante (`<=` → `<`) para ver o TDD falhar | **Revisão pelo GitHub.** A dupla tentou abrir a branch no VS Code do laboratório, mas o clone local apontava para outro repositório; passou então a acompanhar os commits, os arquivos e os PRs pela interface do GitHub | O computador do laboratório não tinha o clone do repositório da dupla, e o GitHub mostra o mesmo histórico que o professor vai avaliar |
| Integração | Conferir o PR da branch de trabalho para a `main`; o assistente revisou também a arquitetura feita pelo outro integrante | Lista de contradições com domínio, testes e portal (REST × eventos, origem dos dados do Painel, gatilho do aviso), itens sem requisito (AI Gateway, Singleton), RabbitMQ fora do `compose` e commits fora do padrão Conventional Commits; **recomendação de ajustar a arquitetura** | **Recomendação descartada:** a dupla decidiu manter a arquitetura como referência e refazer domínio, testes, portal e implementação a partir dela | A arquitetura foi o último documento feito por um integrante e já estava na `main`; a dupla preferiu alinhar os outros documentos a ela a reescrever o trabalho do colega |
| Modelagem | Refazer o domínio com base na arquitetura | RF05 passa para a Garantia de Prazo (`ValidacaoAusencia`, Strategy); RNF01 inteiro no Coletor (UDP + TCP); Frete informa prazo, frete e tipo de cliente; saldo de créditos na Garantia; `NotificacaoSolicitada` como único gatilho de aviso | **Aceito** | A arquitetura não tem ligação entre o Coletor e a Garantia além da fila e do banco, e coloca a validação de ausência como Strategy separada do cálculo. Isso **reverte a decisão anterior** de deixar o RF05 no Rastreamento |
| Testes | Refazer o plano com base na arquitetura | Dublês trocados para os clientes REST do Frete e do Faturamento e para a publicação na fila; casos novos de idempotência no Faturamento (CT34), telemetria com perda (CT37) e saldo (CT38); remoção dos casos de espera pelo veredito | **Aceito** | Os casos precisam verificar as comunicações que a arquitetura realmente usa |
| Tela | Refazer o portal com base na arquitetura | Carga inicial por REST no Pedidos, no Frete e na Garantia e dois canais SSE (Frete e Garantia), no lugar do BFF com um único SSE | **Aceito** | É o desenho da arquitetura; o BFF não existe nela |
| Implementação | Alinhar a implementação com a arquitetura | Trocar o `RegistroPoliticas` por uma `FabricaPoliticas` (Factory), em TDD: teste novo em vermelho, depois o `refactor:` | **Aceito** | A arquitetura usa Strategy + Factory; o código passa a usar os mesmos nomes. As regras do RF02 ao RF04 não mudaram, e os 18 testes continuam passando |
| Arquitetura | Elaboração do `02-arquitetura.md` e do diagrama pelo outro integrante, com apoio de um assistente de IA | Não registrado em detalhe | Documento adotado como referência para os demais (ver a linha "Integração") | O integrante não registrou o que foi sugerido pelo assistente nem o que foi aceito ou descartado nessa entrega |

## Sugestões descartadas ou corrigidas

- **`PoliticaCompensacao` como agregado** (sugestão inicial do assistente): descartada, porque a
  política não tem estado nem ciclo de vida.
- **Exemplo do template com 1h59 como único caso de limite:** substituído por 2h00 e 2h01.
- **Atraso em minutos inteiros sem regra de arredondamento** (primeira versão do plano):
  corrigido para arredondamento para cima, depois que a revisão gerada por outro assistente mostrou que 2h00m30s
  seria truncado e perderia o crédito.
- **Aviso de crédito disparado por `CreditoConcedido` e por `NotaDeCreditoEmitida`** (primeira
  versão do mapa): corrigido para um gatilho único, para o cliente não receber dois avisos.
- **Ajustar a arquitetura ao domínio** (recomendação do assistente na integração): descartada.
  A dupla manteve a arquitetura e alinhou os outros documentos a ela.
- **RF05 no Rastreamento, com o evento `AusenciaComprovada`** (primeira modelagem): substituído
  pela `ValidacaoAusencia` na Garantia, para seguir a arquitetura.
- **BFF do Portal com um único canal SSE** (primeira versão da tela): substituído por dois
  canais SSE, do Frete e da Garantia, como na arquitetura.
- **Arquivos de cache do Python** incluídos por engano nos commits da implementação: removidos
  do histórico antes do push, e um `.gitignore` foi adicionado.
