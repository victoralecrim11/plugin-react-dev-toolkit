# Agentic workflow portatil — Claude Code e Codex

Esta referencia e a fonte canonica dos contratos agenticos do React Dev Hub. No Claude Code, os roles tambem existem como subagents nativos em `agents/`. No Codex, o mesmo comportamento deve ser executado pela skill `react-dev` e pelas tools disponiveis, sem depender de um mecanismo de subagent especifico.

## Routing

- SIMPLE: execute diretamente com a referencia tecnica necessaria.
- STANDARD: planeje ownership, checkpoints e validacao proporcional.
- COMPLEX: use Design-First + Implementation + Build + QA + Review + Security + Quality Gate.

Para STANDARD/COMPLEX, Planner-First e contrato normativo: o planejamento deve existir antes do primeiro side effect relevante.

## Roles logicos

- project-orchestrator: classifica e produz Delegation Plan.
- design-researcher: Research Evidence apenas.
- design-director: DESIGN.md e .design/design-system.md.
- implementation-engineer: implementacao.
- qa-engineer: QA funcional e regressao.
- review: code review tecnico.
- auditar-seguranca: Security Evidence.
- quality-auditor: consolida o Delivery Report e emite Quality Gate.

Nested delegation nunca e requisito. O modelo principal continua sendo Runtime Delegator, Workflow State Host e Handoff Transport.

## Classificacao canonica

Workflow Complexity: SIMPLE | STANDARD | COMPLEX
Architecture Level: BEGINNER | JUNIOR | MID-LEVEL | SENIOR | NOT APPLICABLE
Agentic Execution: AVAILABLE | PARTIAL | UNAVAILABLE | UNKNOWN
Execution Mode: DIRECT | SKILL_CHAIN | AGENTIC | FALLBACK
Agentic Topology: ROOT_ROUTED | DIRECT_ONLY | NESTED | UNKNOWN
Tool Execution Topology: SPECIALIST_DIRECT | ROOT_PROXY | MIXED | UNKNOWN

COMPLEX nao implica SENIOR.

## Delegation Plan

Para STANDARD/COMPLEX, registre:

Step:
Logical Owner:
Objective:
Expected Input:
Expected Canonical Output:
Required Evidence:

Se o runtime nao possuir native agents, execute o role como uma etapa isolada, preserve o owner logico e registre o executor real.

## Ownership

Registre artifacts relevantes com:
Artifact
Logical Owner
Original Content Author
Final Content Author
Runtime Delegator
Tool Executor
Tool Execution Role
Semantic Intervention
Evidence

ROOT_PROXY exige canonical output anterior do owner. O Root materializa literalmente. Se alterar semantica, Final Content Author vira MIXED e Semantic Intervention = YES.

## SIDE-EFFECT TRUTH CONTRACT

SPECIALIST SELF-REPORT != PHASE EVIDENCE.

Nunca aceite como prova frases como:
- "arquivo criado";
- "scaffold concluido";
- "npm install executado";
- "build passou";
- "QA passou";

sem tool evidence ou verificacao fisica independente.

### SPECIALIST_DIRECT

Use quando o role realmente executa side effects. Registre artifact/tool/command evidence.

### CANONICAL_OUTPUT

Use quando o role nao pode ou nao deve escrever diretamente.

Design:
DESIGN CANONICAL PACKAGE
Execution Mode: CANONICAL_OUTPUT
Materialization Status: REQUIRED

Implementation:
IMPLEMENTATION CANONICAL PACKAGE
Execution Mode: CANONICAL_OUTPUT
Materialization Status: REQUIRED

O pacote deve conter manifest completo e conteudo integral dos arquivos. O Root materializa como ROOT_PROXY e verifica os artifacts antes de PASS.

## Design-First

Fluxo preferencial para produtos com UI relevante:

requirements
-> design-research
-> design-direction
-> implementation
-> build-validation
-> qa
-> review
-> security
-> quality-gate

design-researcher produz Research Evidence; design-director e o owner de DESIGN.md e .design/design-system.md.

## Build Claim Contract

Build Validation e fase separada. PASS somente com command evidence e exit code 0. Build verde nao prova comportamento funcional.

Se build falhar, prefira:
Build Evidence -> implementation owner -> canonical correction -> materializacao -> rerun.

## QA

QA funcional e independente da implementacao. Ausencia de testes automatizados nao torna QA NOT APPLICABLE. Quando funcionalidade era relevante e nao foi testada, use NOT EXECUTED.

Leia `qa-engineer.md` para a matriz minima.

## Phase status

PENDING | RUNNING | PASS | PASS WITH WARNINGS | FAIL | NOT EXECUTED | NOT APPLICABLE | UNKNOWN

Nenhuma fase desaparece porque foi pulada.

## Delivery Report

DELIVERY REPORT

Requirements: [status]
Evidence: ...

Design: [status]
Evidence: ...

Implementation: [status]
Evidence: ...

Build: [status]
Evidence: ...

QA: [status]
Evidence: ...

Review: [status]
Evidence: ...

Security: [status]
Evidence: ...

## Quality Gate

READY | READY WITH WARNINGS | BLOCKED

Product Quality Status: READY | READY WITH WARNINGS | BLOCKED
Toolkit Compliance Status: COMPLIANT | PARTIAL | FAILED

Compliance trace:
Planner Compliance: COMPLIANT | VIOLATED | NOT APPLICABLE | UNKNOWN
Planner Runtime Enforcement: AVAILABLE | UNAVAILABLE | UNKNOWN
Architecture Compliance: FULL | PARTIAL | VIOLATED | UNKNOWN

Product Quality e Toolkit Compliance sao independentes.

## Finalization check

Antes de declarar sucesso:
- planner/owners e trace correspondem ao observado;
- canonical output existe antes de ROOT_PROXY;
- artifacts foram verificados fisicamente;
- semantic intervention esta registrada;
- Build, QA, Review e Security possuem evidence propria ou status de ausencia;
- quality-auditor apenas consolidou;
- nenhuma afirmacao funcional excede a evidencia.
