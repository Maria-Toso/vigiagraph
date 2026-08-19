# Backlog de evolucao

Este arquivo transforma o roadmap em issues pequenas o bastante para serem implementadas,
testadas e apresentadas separadamente no GitHub.

## Milestone 0.2 — Persistencia profissional

| Issue sugerida | Labels | Criterio de aceite |
| --- | --- | --- |
| Adicionar PostgreSQL ao Docker Compose | `database`, `devops` | API inicia e persiste dados no container |
| Criar migrations com Alembic | `database` | banco vazio chega ao schema atual por migration |
| Implementar repositorio PostgreSQL | `backend` | contrato atual passa nos mesmos testes do SQLite |
| Adicionar filtros por periodo e nivel | `api` | endpoint aceita filtros validados e documentados |

## Milestone 0.3 — Inteligencia por grafos

| Issue sugerida | Labels | Criterio de aceite |
| --- | --- | --- |
| Modelar entidades no Neo4j | `graph`, `architecture` | usuarios, cartoes, IPs, dispositivos e lojistas possuem relacoes |
| Sincronizar transacoes com o grafo | `graph`, `backend` | nova transacao cria ou atualiza nos e arestas idempotentemente |
| Detectar comunidades suspeitas | `graph`, `fraud-rule` | consulta Cypher retorna grupos densamente conectados |
| Exibir caminho de conexoes no caso | `graph`, `frontend` | dashboard mostra por que duas entidades estao relacionadas |

## Milestone 0.4 — Machine learning

| Issue sugerida | Labels | Criterio de aceite |
| --- | --- | --- |
| Criar pipeline de features | `data`, `ml` | dataset versionado e reproduzivel a partir de uma seed |
| Treinar baseline Isolation Forest | `ml` | script salva modelo, parametros e metricas |
| Avaliar classificacao | `ml`, `evaluation` | relatorio inclui precision, recall, F1 e matriz de confusao |
| Adicionar sinal do modelo ao score | `ml`, `backend` | resposta informa versao, contribuicao e explicacao do modelo |

## Milestone 0.5 — Operacao em tempo real

| Issue sugerida | Labels | Criterio de aceite |
| --- | --- | --- |
| Processar eventos em fila | `backend`, `devops` | worker processa transacoes sem bloquear a API |
| Criar autenticacao JWT | `security`, `api` | rotas privadas exigem token valido |
| Implementar gestao de casos | `feature`, `frontend` | analista altera status e registra observacoes auditaveis |
| Adicionar metricas e tracing | `observability` | latencia, erros e volume aparecem em dashboard tecnico |

## Ordem recomendada

Conclua uma milestone por vez e publique uma release ao final de cada uma. Cada pull request deve
resolver uma unica issue e incluir testes. Isso cria um historico de evolucao legivel para quem
avaliar o portfolio, em vez do celebre commit `projeto final agora vai 7`.

