# React Dev Hub Plugin

Plugin local para orientar e construir projetos React, Next.js e React Native/Expo com TypeScript. Reúne comandos de scaffolding, arquitetura e review, além de um Project Hub que persiste dados localmente em JSON.

## Estrutura

- `commands/`: `/setup`, `/criar-projeto`, `/criar-componente`, `/review`, `/arquitetura` e `/dashboard`.
- `skills/react-core/`: regras comuns de React moderno.
- `skills/nextjs-extension/` e `skills/react-native-extension/`: particularidades por plataforma.
- `skills/react-project-builder/`: fluxo didático de discovery até review.
- `skills/dashboard-projetos/`: painel local e seus arquivos de referência.

## Dashboard local

Copie os quatro arquivos de `skills/dashboard-projetos/references/` para a pasta que guardará os dados e execute `iniciar-dashboard.bat` no Windows, ou dê permissão e execute `./iniciar-dashboard.command` no macOS/Linux. Abra `http://127.0.0.1:8766`.

O arquivo `projetos-data.json` é criado automaticamente ao salvar o primeiro item. Ele contém somente os dados locais de projetos, componentes, reviews e checklists.

## Princípios

TypeScript obrigatório, componentes funcionais, Hooks, Context/Zustand para estado local-global conforme a necessidade e TanStack Query para estado remoto. O plugin prioriza MVP, justificativa técnica e aprendizado antes de complexidade arquitetural.
