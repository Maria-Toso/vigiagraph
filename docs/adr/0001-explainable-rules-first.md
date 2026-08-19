# ADR 0001: Regras explicaveis antes de machine learning

- Status: aceito
- Data: 2026-08-19

## Contexto

O projeto precisa entregar valor antes de possuir um conjunto de dados rotulado confiavel. Um
modelo treinado apenas com dados artificiais poderia parecer sofisticado, mas sua qualidade nao
representaria uso real.

## Decisao

A primeira versao utiliza regras deterministicas. Toda regra produz um codigo, peso, descricao
e evidencias. Machine learning sera adicionado como sinal complementar depois que o pipeline de
dados e as metricas de avaliacao estiverem definidos.

## Consequencias

- O MVP pode ser executado e compreendido imediatamente.
- Testes conseguem verificar cada decisao de forma deterministica.
- Analistas recebem uma explicacao auditavel.
- A versao inicial nao aprende novos padroes automaticamente.
- Pesos e limites ainda precisam de calibracao antes de qualquer uso real.

