# Contribuindo com o VigiaGraph

Obrigada por considerar uma contribuicao. O projeto prioriza codigo legivel, testes e decisoes
de risco que possam ser explicadas para uma pessoa — nao apenas para um notebook muito confiante.

## Preparacao

1. Crie um fork e uma branch a partir de `main`.
2. Instale o ambiente de desenvolvimento com `python -m pip install -e ".[dev]"`.
3. Implemente a mudanca e adicione ou atualize os testes.
4. Execute `ruff check .` e `pytest` antes de abrir o pull request.

## Convencoes

- Use nomes claros em ingles no codigo e documentacao em portugues quando voltada ao usuario.
- Mantenha regras de risco pequenas, deterministicas e acompanhadas de evidencia.
- Nao inclua dados financeiros ou pessoais reais em testes, exemplos ou issues.
- Registre decisoes arquiteturais relevantes em `docs/adr/`.

## Commits

Prefira commits pequenos e objetivos. Exemplos:

- `feat: add velocity rule for merchant transactions`
- `fix: preserve timezone when loading transaction history`
- `test: cover shared IP risk evidence`
- `docs: explain Neo4j migration strategy`

## Pull requests

Descreva o problema, a solucao escolhida, como validar e qualquer risco conhecido. Mudancas no
score precisam informar se alteram os limites ou o comportamento de regras existentes.

