# React Dev Hub Plugin — v1.2.1

Plugin de desenvolvimento orientado a aprendizado para planejar, construir, revisar e acompanhar projetos **React, Next.js e React Native/Expo**. Combina padrões modernos de TypeScript com decisões arquiteturais proporcionais ao nível do desenvolvedor e ao tamanho do produto.

## O ciclo de desenvolvimento

O fluxo tem frequências distintas: `/setup` roda **uma vez por máquina**, `/criar-projeto` **uma vez por projeto**, e os demais são de uso recorrente durante o desenvolvimento.

1. `/setup` — **configuração do ambiente.** Registra seu nível de calibração (Beginner/Junior/Mid-Level/Senior), a pasta-base dos projetos e as preferências padrão de stack. Em seguida entrega as ferramentas locais: sobe o **Project Hub** e disponibiliza o **manual interativo**. Não gera código. É idempotente — rodar de novo é a forma de alterar o perfil.
2. `/criar-projeto` — **uma vez por projeto.** Lê o perfil salvo pelo `/setup` e pergunta apenas o que é específico do projeto: nome, plataforma, objetivo e escopo. Transforma a ideia em scaffold TypeScript com estrutura de pastas, arquivos fundamentais e próximos passos.
3. `/criar-componente` — produz componentes e hooks reutilizáveis, pequenos, acessíveis e tipados. Itens com potencial de reuso podem ser adicionados ao catálogo do dashboard.
4. `/arquitetura` — define ou ajusta a organização de pastas, estado e responsabilidades sem antecipar complexidade que o projeto ainda não precisa.
5. `/review` — analisa código existente, preserva comportamento e registra manutenibilidade, riscos e débitos técnicos no Project Hub.
6. `/dashboard` — reabre o painel local a qualquer momento para consultar projetos, componentes, reviews e checklists arquiteturais.

### Perfil persistido

O nível de calibração é informado no `/setup` e fica em `dashboard-config.json`. Todos os comandos **leem** esse valor para ajustar a profundidade das explicações e o teto de complexidade arquitetural — nenhum deles repergunta o seu nível a cada projeto novo, e nenhum deles escreve nele.

| Campo | Função |
| --- | --- |
| `devLevel` | Beginner, Junior, Mid-Level ou Senior |
| `projectsRoot` | Pasta-base onde os projetos ficam |
| `defaultPlatform` | `react`, `next` ou `expo` (padrão, sobrescrevível por projeto) |
| `defaultGoal` | `academico`, `mvp` ou `producao` |
| `scanRoot` | Raiz usada pelo scan do painel; mantida igual a `projectsRoot` |
| `setupCompletedAt` | Marca que o onboarding já rodou |

### Alterando o perfil depois

Rode `/setup` novamente. Ele detecta que o perfil já existe e entra em **modo reconfiguração**: mostra o que está salvo, pergunta só o que você quer mudar, grava via merge parcial e pula a instalação. Nada é reinstalado e nenhum outro campo é perdido.

Trocar o `devLevel` afeta o teto de complexidade dos próximos comandos, mas não reescreve projetos já criados. Se você mudar `projectsRoot`, o `/setup` move o Project Hub e os dados para a nova pasta.

Se o perfil não existir, os comandos avisam, assumem `Junior` como nível provisório e seguem o trabalho — nenhum deles refaz o onboarding por conta própria.

## Padrões técnicos

O plugin não usa componentes de classe, bibliotecas legadas ou TypeScript opcional. A recomendação padrão é sempre explicada com motivo, alternativas, trade-offs e situações em que ela não é indicada.

### React Core

- **TypeScript estrito** para tornar contratos e refatorações mais seguros.
- **Componentes funcionais e Hooks** para composição clara e compatível com o React moderno.
- **Context API** para dependências globais estáveis e simples.
- **Zustand** somente quando há estado global compartilhado e mutável; evita a complexidade de Redux quando ela não é necessária.
- **TanStack Query** para dados remotos: cache, carregamento, erro, invalidação e sincronização não pertencem ao estado global da interface.

### Next.js

Usa App Router. Server Components são preferidos para leitura e composição sem interatividade; `"use client"` aparece apenas na fronteira necessária. Server Actions atendem mutações simples de formulário, enquanto Route Handlers continuam adequados para APIs públicas e integrações externas. A estratégia de SSR, SSG ou renderização dinâmica é escolhida de acordo com SEO, cache e natureza dos dados.

### React Native / Expo

Prioriza Expo managed workflow, Expo Router, Hermes, TypeScript, Reanimated e Gesture Handler. Bare Workflow só é sugerido quando uma integração nativa ou requisito de build realmente não é suportado pelo Expo. O plugin considera permissões, acessibilidade, inicialização, diferentes telas e uso offline desde o planejamento.

## Arquitetura que evolui com o projeto

| Nível | Quando usar | Estrutura recomendada |
| --- | --- | --- |
| Beginner | Projeto acadêmico, portfólio ou MVP pequeno | `components`, `screens`, `repositories`, `theme`, `types` |
| Junior | Mais telas, formulários ou reaproveitamento de lógica | Adiciona `hooks` e `utils` |
| Mid-Level | Múltiplas funcionalidades, integrações ou equipe | Adiciona `features`, `store` e `shared` |
| Senior | Domínio complexo e evolução de longo prazo | Modularização avançada somente com justificativa |

DDD, Clean Architecture, CQRS e abstrações corporativas não são ponto de partida. Uma versão funcional, legível e testável vale mais do que uma arquitetura sofisticada incompleta.

## Dashboard local — Project Hub

O pacote inclui um painel independente, implementado com Python padrão e HTML/JavaScript. Não há banco de dados, login nem serviço externo: tudo fica na pasta em que você executar os arquivos.

O painel em `http://127.0.0.1:8766` permite:

- Cadastrar projetos React, Next.js e Expo com status, versão do React, stack e nível de senioridade.
- Manter um catálogo de componentes e decisões de design system reutilizáveis.
- Registrar code reviews, pontuação de manutenibilidade e débitos técnicos.
- Acompanhar um checklist de qualidade e arquitetura por projeto.
- Editar e excluir os registros diretamente pela interface.

### Como iniciar

O caminho recomendado é rodar `/setup`: ele copia os arquivos, sobe o servidor e abre o painel para você. Se preferir fazer à mão:

1. Copie os arquivos de `skills/dashboard-projetos/references/` para a pasta onde deseja manter os dados do Project Hub.
2. No Windows, dê duplo clique em `iniciar-dashboard.bat`.
3. No macOS/Linux, execute `chmod +x iniciar-dashboard.command` uma vez e depois `./iniciar-dashboard.command`.
4. O navegador abre automaticamente em `http://127.0.0.1:8766`.

Depois disso, `/dashboard` reabre o painel a qualquer momento.

O único requisito é Python 3 instalado. O servidor usa somente a biblioteca padrão; não é necessário instalar pacotes com `pip`.

### Onde ficam os dados

Dois arquivos ficam ao lado de `dashboard-server.py`:

- **`projetos-data.json`** — projetos, componentes, reviews e checklists. Criado **quando o primeiro registro é salvo**; antes disso a tela usa uma estrutura vazia em memória, por isso não há arquivo ao abrir o dashboard pela primeira vez.
- **`dashboard-config.json`** — seu perfil (`devLevel`, `projectsRoot`, plataforma e objetivo padrão) e as preferências de scan. Escrito pelo `/setup`.

Para fazer backup, copie os dois. Para reiniciar o Project Hub, feche o servidor e exclua `projetos-data.json` — isso apaga permanentemente os registros do painel, mas não altera seus projetos de código. Excluir `dashboard-config.json` faz o `/setup` rodar o onboarding do zero.

## Estrutura do pacote

```text
plugin-react-dev/
├── .agents/plugins/              # Marketplace padrão do Codex
├── .codex-plugin/                 # Manifesto do Codex
├── .claude-plugin/                # Metadados legados de compatibilidade
├── commands/                      # Comandos de fluxo de trabalho
├── skills/
│   ├── react-core/                # Padrões compartilhados
│   ├── nextjs-extension/          # Particularidades do Next.js
│   ├── react-native-extension/    # Particularidades do Expo/RN
│   ├── react-project-builder/     # Discovery, MVP, implementação e review
│   └── dashboard-projetos/        # Project Hub e arquivos de referência
├── manual.html                    # Manual visual de consulta rápida
└── README.md
```

## Princípios de mentoria

O plugin atua como parceiro de desenvolvimento, não apenas como gerador de código. Para ideias vagas, primeiro ajuda a definir público, objetivo, MVP, riscos e viabilidade. Para implementação, trabalha de maneira incremental e explica decisões de acordo com o nível do desenvolvedor.

Em cada review, a análise considera: tipagem, tratamento de erro, estados de carregamento, acessibilidade, nomes, separação de responsabilidades, segurança, re-renderizações, cache, tamanho de bundle e cobertura de testes.

## Manual

Abra `manual.html` no navegador para uma visão rápida dos comandos e do fluxo recomendado. O manual e este README acompanham a versão do plugin e podem ser mantidos junto à sua pasta de projetos.

## Instalação no Codex

Este repositório é também o diretório do plugin. O marketplace padrão fica em `.agents/plugins/marketplace.json` e aponta para `./`, isto é, para a raiz do repositório onde estão `.codex-plugin/plugin.json` e `skills/`.

Para testar uma cópia local, adicione a raiz do repositório como marketplace local e reinicie o aplicativo. Para distribuir via GitHub, use este repositório como marketplace e mantenha o arquivo `.agents/plugins/marketplace.json` no branch publicado. Em repositórios privados, o Git usado pelo Codex precisa ter credenciais de leitura para a sua conta; a estrutura do plugin, porém, é a mesma.
