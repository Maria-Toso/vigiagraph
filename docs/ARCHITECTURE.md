# Arquitetura do VigiaGraph

## Objetivo

Separar a decisao antifraude da tecnologia usada para entregar ou armazenar essa decisao. O
motor de risco pode ser testado sem API, banco ou rede, reduzindo o custo das proximas evolucoes.

## Componentes

| Camada | Responsabilidade | Implementacao atual |
| --- | --- | --- |
| Domain | transacao, regra acionada e avaliacao de risco | dataclasses e enums |
| Services | regras, score e dados sinteticos | Python puro |
| Infrastructure | persistencia e consultas | SQLite |
| API | validacao e endpoints REST | FastAPI + Pydantic |
| Web | visualizacao operacional | HTML, CSS e JavaScript |

## Fluxo de analise

1. A API valida o payload recebido.
2. O repositorio recupera o historico conhecido.
3. O motor executa cada regra contra a transacao e o historico.
4. Cada regra retorna peso, descricao e evidencias verificaveis.
5. O score e limitado a 100 e convertido em nivel de risco.
6. A transacao e a avaliacao sao persistidas juntas.
7. A API devolve a decisao explicada ao cliente.

## Evolucao para grafos

Neo4j sera um adaptador adicional, nao o banco principal. PostgreSQL guardara o registro
transacional; Neo4j representara conexoes entre usuarios, cartoes, dispositivos, IPs e lojistas.
Um novo servico de features consultara essas conexoes e entregara sinais ao mesmo motor de risco.

## Evolucao para machine learning

Modelos nao substituirao imediatamente as regras. O primeiro modelo sera treinado offline com
dados sinteticos e avaliado por precision, recall, F1 e matriz de confusao. A inferencia gerara
um novo sinal explicavel, versionado e monitorado, mantendo as regras como baseline.

