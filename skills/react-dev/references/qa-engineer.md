# QA Engineer — validacao funcional baseada em evidencia

Use esta referencia na fase QA de workflows STANDARD/COMPLEX ou quando o usuario pedir testes funcionais/E2E.

## Principio

QA deve verificar comportamento observavel. Build, lint e typecheck nao substituem QA.

## Para cada cenario

Scenario:
Expected:
Observed:
Status: PASS | PASS WITH WARNINGS | FAIL | NOT EXECUTED | NOT APPLICABLE | UNKNOWN
Evidence:

## Matriz minima para interfaces

Quando aplicavel, cubra:
- loading;
- empty;
- error;
- success;
- acao principal do usuario;
- validacao de formularios;
- filtros/estado;
- atualizacao de dados apos mutacao;
- keyboard;
- foco inicial e retorno de foco em dialogs;
- Escape;
- desktop;
- mobile;
- overflow horizontal;
- regressao do comportamento alterado.

## Regras

- Nao marque PASS por inspecao de codigo quando o cenario exige execucao.
- Nao declare WCAG compliance completa sem auditoria apropriada.
- Registre limites de browser/device/cobertura.
- Se o app nao existe fisicamente ou nao inicia, QA = FAIL/NOT EXECUTED conforme a evidencia; nunca invente resultados.

## Output

QA RESULT
Status:
Scenarios:
Warnings:
Blockers:
Evidence Summary:
