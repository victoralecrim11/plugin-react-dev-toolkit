# React Dev Hub Plugin — v1.5.3
> Compatível com **Claude Code / Claude Desktop** (`.claude-plugin/`) e com o **Codex** (`.codex-plugin/`), a partir de um único repositório.

Plugin de desenvolvimento orientado a aprendizado para planejar, construir, revisar, publicar e acompanhar projetos **React, Next.js e React Native/Expo**. Combina padrões modernos de TypeScript com decisões arquiteturais proporcionais ao nível do desenvolvedor e ao tamanho do produto. Inclui o comando `/gerar-midia` para criar imagens hero, previews sociais e vídeos curtos via MCP da Higgsfield, o `/analisar-projeto-gsd`, que analisa projetos construídos com o **framework GSD** cruzando os artefatos da pasta `.planning/` com o código real, e o `/auditar-seguranca`, uma auditoria de segurança que caça as brechas típicas de "vibe coding" antes que virem problema.

```shell
/plugin marketplace add victoralecrim11/plugin-react-dev-toolkit
/plugin install plugin-react-dev-toolkit@react-dev-marketplace
/reload-plugins
```

Depois: `/plugin-react-dev-toolkit:setup`. As outras formas de instalar estão em [Instalação](#instalação).

## Índice

- [React Dev Hub Plugin — v1.5.3](#react-dev-hub-plugin--v153)
  - [Índice](#índice)
  - [Instalação](#instalação)
    - [Claude Code (CLI)](#claude-code-cli)
    - [Claude Desktop](#claude-desktop)
    - [Desenvolvimento local (sem publicar)](#desenvolvimento-local-sem-publicar)
    - [Codex](#codex)
    - [Comandos após a instalação](#comandos-após-a-instalação)
    - [Atualizar depois de um push](#atualizar-depois-de-um-push)
      - [Na sua máquina](#na-sua-máquina)
      - [Deixar o Claude Code atualizar sozinho](#deixar-o-claude-code-atualizar-sozinho)
  - [O ciclo de desenvolvimento](#o-ciclo-de-desenvolvimento)
    - [O fluxo do `/deploy`](#o-fluxo-do-deploy)
  - [A skill que age sozinha](#a-skill-que-age-sozinha)
  - [Perfil persistido](#perfil-persistido)
    - [Alterando o perfil depois](#alterando-o-perfil-depois)
  - [Padrões técnicos](#padrões-técnicos)
    - [React Core](#react-core)
    - [Next.js](#nextjs)
    - [React Native / Expo](#react-native--expo)
  - [Arquitetura que evolui com o projeto](#arquitetura-que-evolui-com-o-projeto)
  - [Dashboard local — Project Hub](#dashboard-local--project-hub)
    - [Como iniciar](#como-iniciar)
    - [Onde ficam os dados](#onde-ficam-os-dados)
  - [Estrutura do pacote](#estrutura-do-pacote)
  - [Princípios de mentoria](#princípios-de-mentoria)
  - [Manual](#manual)
  - [O que mudou na v1.5.1](#o-que-mudou-na-v151)
  - [O que mudou na v1.5.0](#o-que-mudou-na-v150)
  - [O que mudou na v1.4.0](#o-que-mudou-na-v140)
  - [O que mudou na v1.3.12](#o-que-mudou-na-v11312)
  - [O que mudou na v1.3.2](#o-que-mudou-na-v132)
  - [O que mudou na v1.3.1](#o-que-mudou-na-v131)
  - [O que mudou na v1.3.0](#o-que-mudou-na-v130)
  - [Licença](#licença)

## Instalação

O repositório é, ao mesmo tempo, **o plugin e o marketplace**. Os dois manifestos (`.claude-plugin/` e `.codex-plugin/`) apontam para a mesma raiz, então um único `git push` publica para os dois ecossistemas.

| | Nome |
| :-- | :-- |
| Marketplace (Claude Code) | `react-dev-marketplace` |
| Plugin / namespace | `plugin-react-dev-toolkit` |

Requisitos: **Claude Code 2.1.128+** para carregar um `.zip` com `--plugin-dir`, **2.1.193+** para a migração automática de nome descrita no fim desta seção, e **Python 3** para o Project Hub (só biblioteca padrão, sem `pip`).

### Claude Code (CLI)

```shell
/plugin marketplace add victoralecrim11/plugin-react-dev-toolkit
/plugin install plugin-react-dev-toolkit@react-dev-marketplace
/reload-plugins
```

Formas alternativas de adicionar o marketplace:

```shell
# URL git completa (qualquer host: GitHub, GitLab, Bitbucket, self-hosted)
/plugin marketplace add https://github.com/victoralecrim11/plugin-react-dev-toolkit.git

# fixando uma tag ou branch
/plugin marketplace add https://github.com/victoralecrim11/plugin-react-dev-toolkit.git#v1.3.2

# URL direta do marketplace.json
/plugin marketplace add https://raw.githubusercontent.com/victoralecrim11/plugin-react-dev-toolkit/main/.claude-plugin/marketplace.json
```

> A última forma tem uma limitação: um marketplace adicionado por URL direta baixa **apenas o JSON**. Como a entrada deste plugin usa `"source": "./"` (caminho relativo), prefira `owner/repo` ou a URL `.git`, que clonam o repositório inteiro e resolvem o caminho corretamente.

### Claude Desktop

No app desktop, clique no botão **+** ao lado da caixa de prompt → **Plugins** → **Add plugin**. O navegador de plugins lista os marketplaces já configurados. Marketplaces adicionados pela CLI (`/plugin marketplace add`) aparecem lá, então o caminho mais direto é adicionar o marketplace uma vez via CLI e depois instalar/gerenciar pelo desktop. Use **Manage plugins** para habilitar, desabilitar ou remover.

O navegador de plugins não existe em sessões cloud nem WSL. Para sessões cloud, declare o plugin no `.claude/settings.json` do repositório:

```json
{
  "extraKnownMarketplaces": {
    "react-dev-marketplace": {
      "source": {
        "source": "github",
        "repo": "victoralecrim11/plugin-react-dev-toolkit"
      }
    }
  },
  "enabledPlugins": ["plugin-react-dev-toolkit@react-dev-marketplace"]
}
```

### Desenvolvimento local (sem publicar)

```shell
# a partir da pasta-pai do repositório
claude --plugin-dir ./plugin-react-dev-toolkit

# ou um zip do diretório (Claude Code 2.1.128+)
claude --plugin-dir ./plugin-react-dev-toolkit.zip

# ou o repositório como marketplace local
/plugin marketplace add ./plugin-react-dev-toolkit
```

Depois de editar qualquer arquivo, rode `/reload-plugins`. O resumo conta apenas o diretório `commands/`, então pode exibir `0 skills` mesmo tendo recarregado as skills de `skills/`.

Valide antes de publicar ou submeter à comunidade:

```shell
claude plugin validate .
```

Se algo não carregar, abra `/plugin` e veja a aba **Errors**.

### Codex

O marketplace padrão do Codex fica em `.agents/plugins/marketplace.json` e usa `source: "url"` apontando para o repositório GitHub da raiz do plugin. Esse formato é o recomendado para plugins hospedados em Git, porque o Codex faz o clone e precisa resolver a origem a partir do repositório remoto. Para desenvolvimento local, use o exemplo em `examples/codex-marketplace-local.json` e ajuste o `path` para a pasta onde clonou o repositório. Em repositórios privados, o Git usado pelo Codex precisa ter credenciais de leitura para a sua conta.

#### Codex CLI

A instalação do plugin no Codex CLI não usa os mesmos comandos `/plugin` do Claude Code. Use o marketplace do Codex para registrar este repositório e instalar ou atualizar o plugin a partir dele.

```shell
codex plugin marketplace add https://raw.githubusercontent.com/victoralecrim11/plugin-react-dev-toolkit/main/.codex-plugin/marketplace.json
codex plugin marketplace upgrade
```

Se você já tiver o marketplace configurado, basta rodar `codex plugin marketplace upgrade` e reiniciar o app. O `codex plugin marketplace add` registra o marketplace; a instalação efetiva do plugin ocorre via marketplace e o app carrega os comandos a partir dele.

### Comandos após a instalação

No Claude Code os comandos de plugin são **namespaced** pelo nome do plugin, para evitar conflito entre plugins:

| Comando | | Frequência |
| :-- | :-- | :-- |
| `/plugin-react-dev-toolkit:setup` | configuração do ambiente e do perfil | uma vez por máquina |
| `/plugin-react-dev-toolkit:criar-projeto` | scaffolding de um novo projeto | uma vez por projeto |
| `/plugin-react-dev-toolkit:criar-componente` | componentes, hooks e testes | recorrente |
| `/plugin-react-dev-toolkit:arquitetura` | organização de pastas, estado e responsabilidades | recorrente |
| `/plugin-react-dev-toolkit:review` | code review didático | recorrente |
| `/plugin-react-dev-toolkit:auditar-seguranca` | auditoria de segurança: segredos, deps, XSS, injeção, auth | recorrente |
| `/plugin-react-dev-toolkit:analisar-projeto-gsd` | analisa um projeto feito com o framework GSD (spec `.planning/` vs código) | recorrente |
| `/plugin-react-dev-toolkit:deploy` | análise da stack, build e publicação | fim de ciclo |
| `/plugin-react-dev-toolkit:gerar-midia` | gera imagem hero, OG image ou vídeo curto com MCP da Higgsfield | opção criativa |
| `/plugin-react-dev-toolkit:dashboard` | reabre o Project Hub | recorrente |

No Codex os mesmos comandos não levam prefixo: `/setup`, `/criar-projeto`, e assim por diante. O `manual.html` tem um alternador que reescreve a página inteira para o contexto que você escolher.

> **Renomeação:** o plugin se chamava `plugin-react-dev` até a v1.2.1. O `marketplace.json` traz um mapa `renames` que migra instalações antigas automaticamente (Claude Code 2.1.193+). Em versões anteriores, remova e reinstale o plugin.

### Atualizar depois de um push

As duas plataformas decidem se há atualização comparando o campo `version` dos manifestos. Por isso o repositório tem um workflow que **bumpa o patch e sincroniza a versão nos quatro lugares** a cada push na `main` — você commita normal, a Action publica.

```
.github/workflows/bump-version.yml   # bump + validação + tag, no push da main
scripts/bump-version.py              # sincroniza a versão nos 4 manifestos
scripts/validate-plugin.py           # checagens de estrutura, roda no CI
scripts/atualizar-plugin.ps1 / .sh   # atualiza sua máquina nas 2 plataformas
```

O workflow valida antes de taguear: as checagens próprias, o `claude plugin validate . --strict` oficial, e o `claude plugin tag --dry-run`, que confirma que `plugin.json` e a entrada do marketplace concordam na versão. Se qualquer uma falhar, nada é publicado.

Para pular o bump num commit só de documentação, o workflow já ignora mudanças em `**/*.md`, `manual.html`, `LICENSE`, `.github/**` e `scripts/**`. Para forçar um `minor` ou `major`, use **Actions → Bump da versao do plugin → Run workflow** e escolha a parte.

#### Na sua máquina

```shell
# Windows
pwsh scripts/atualizar-plugin.ps1

# macOS / Linux
./scripts/atualizar-plugin.sh
```

O script roda o que cada plataforma precisa:

| | Comando | Recarrega sessão aberta? |
| :-- | :-- | :-- |
| Claude Code | `claude plugin marketplace update react-dev-marketplace` + `claude plugin update plugin-react-dev-toolkit@react-dev-marketplace` | Não — rode `/reload-plugins` |
| Codex | `codex plugin marketplace upgrade` | Não — reinicie o app |

Se algo ficar preso numa versão antiga, `--limpar-cache` (ou `-LimparCache`) apaga `~/.claude/plugins/cache` e `~/.codex/plugins/cache` antes de atualizar.

#### Deixar o Claude Code atualizar sozinho

O Claude Code atualiza marketplaces e plugins em background depois que a sessão inicia, mas **vem desligado para marketplaces de terceiros** — precisa ligar uma vez:

1. `/plugin` → aba **Marketplaces**
2. selecione `react-dev-marketplace`
3. **Enable auto-update**

A checagem roda com atraso aleatório de até dez minutos após o início da sessão, e a sessão em andamento continua usando o que carregou no launch: quando houver atualização, aparece um aviso para rodar `/reload-plugins`.

No **Codex não existe auto-update documentado** para plugins de marketplace. O caminho é o `codex plugin marketplace upgrade` do script. Para a instalação via GitHub, o marketplace usa `source: "url"` e a atualização vem do `upgrade`; para desenvolvimento local, o exemplo em `examples/codex-marketplace-local.json` aponta para a pasta do clone local.

## O ciclo de desenvolvimento

O fluxo tem frequências distintas: `/setup` roda **uma vez por máquina**, `/criar-projeto` **uma vez por projeto**, e os demais são de uso recorrente durante o desenvolvimento.

> Os nomes abaixo aparecem sem prefixo por legibilidade. No Claude Code, acrescente `plugin-react-dev-toolkit:` — veja [Comandos após a instalação](#comandos-após-a-instalação).

1. `/setup` — **configuração do ambiente.** Registra seu nível de calibração (Beginner/Junior/Mid-Level/Senior), a pasta-base dos projetos e as preferências padrão de stack. Em seguida entrega as ferramentas locais: sobe o **Project Hub** e disponibiliza o **manual interativo**. Não gera código. É idempotente — rodar de novo é a forma de alterar o perfil.
2. `/criar-projeto` — **uma vez por projeto.** Lê o perfil salvo pelo `/setup` e pergunta apenas o que é específico do projeto: nome, plataforma, objetivo e escopo. Transforma a ideia em scaffold TypeScript com estrutura de pastas, arquivos fundamentais e próximos passos.
3. `/criar-componente` — produz componentes e hooks reutilizáveis, pequenos, acessíveis e tipados. Itens com potencial de reuso podem ser adicionados ao catálogo do dashboard.
4. `/arquitetura` — define ou ajusta a organização de pastas, estado e responsabilidades sem antecipar complexidade que o projeto ainda não precisa.
5. `/review` — analisa código existente, preserva comportamento e registra manutenibilidade, riscos e débitos técnicos no Project Hub. Inclui uma passada de segurança em todo review.
6. `/auditar-seguranca` — auditoria de segurança dedicada e mais profunda que a passada do `/review`. Procura brechas exploráveis — segredos vazados no bundle do cliente, dependências vulneráveis, XSS, injeção, autenticação/autorização frágil e exposição de dados — classifica cada achado por severidade (Crítico/Alto/Médio/Baixo) e, com sua aprovação, corrige preservando comportamento. É o antídoto direto para as brechas típicas de "vibe coding". Registra a postura de segurança no Project Hub.
7. `/analisar-projeto-gsd` — para projetos construídos com o **framework GSD**: lê os artefatos da pasta `.planning/` (visão, requisitos, roadmap e planos das fases) e cruza com o código React/Next/Expo real. Separa os achados em **deriva de spec** (o que o GSD documentou e o código não cumpre) e **qualidade técnica**, e — com sua aprovação — corrige o que fugiu da spec, preservando comportamento. Registra a análise no Project Hub.
8. `/dashboard` — reabre o painel local a qualquer momento para consultar projetos, componentes, reviews e checklists arquiteturais.
9. `/deploy` — **Comando dado SOMENTE após o final do projeto.** Inspeciona silenciosamente a stack do projeto, recomenda o provedor ideal e guia o processo de publicação com segurança e automação.

### O fluxo do `/deploy`

A ordem é obrigatória e existe para não publicar build quebrado nem vazar credencial: **analisar → configurar → validar → confirmar → deploy → informar**. Se o build falhar na etapa de validação, o processo para e reporta o arquivo e a possível correção, em vez de publicar.

Provedores mapeados: **Vercel, Netlify, Cloudflare Pages, GitHub Pages, Expo EAS** e automação via **GitHub Actions**. A recomendação sai da stack detectada — Next.js sugere Vercel, Vite/SPA abre as opções de hosting estático, Expo mobile vai para o EAS.

Credenciais nunca entram no código. Elas ficam no painel do provedor ou em **Settings → Secrets and variables → Actions**.

## A skill que age sozinha

O pacote traz **uma** skill **model-invoked**: `react-dev`. O assistente a aciona por conta própria conforme o assunto, e ela carrega só o arquivo de referência que a tarefa exige.

```text
skills/react-dev/
├── SKILL.md                   # índice: qual assunto -> qual arquivo
└── references/
    ├── react-mentor.md         # mentoria, arquitetura, carreira, tutor e review
    ├── react-core.md          # React, TypeScript, Hooks, estado, dados remotos
    ├── nextjs.md              # App Router, Server Components, Server Actions, SSR
    ├── react-native.md        # Expo, Expo Router, Hermes, Reanimated
    ├── project-builder.md     # discovery, MVP, implementação incremental
    ├── deploy-advisor.md      # deploy, CI/CD, provedores, segredos
    ├── dashboard-projetos.md  # schema da API do Project Hub
    └── project-hub/           # o servidor local e o template
```

`SKILL.md` tem `user-invocable: false`, então não aparece no menu `/`. E como é **uma** skill, o painel do plugin lista `react-dev` em vez de seis nomes.

Isso importa por dois motivos:

- **Nada de `/…-extension` em canto nenhum.** Todo `SKILL.md` é um componente e aparece no painel do plugin — nenhum campo de frontmatter esconde isso. A única forma de não ver seis nomes ali é não ter seis skills.
- **Menos contexto sempre ligado.** Seis descrições de skill custavam ~428 tokens em toda sessão; uma custa ~364.

## Perfil persistido

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

1. Copie os arquivos de `skills/react-dev/references/project-hub/` para uma subpasta `ProjectHUB` dentro da pasta onde deseja manter os dados do Project Hub.
2. No Windows, dê duplo clique em `ProjectHUB\iniciar-dashboard.bat`.
3. No macOS/Linux, execute `chmod +x ProjectHUB/iniciar-dashboard.command` uma vez e depois `./ProjectHUB/iniciar-dashboard.command`.
4. O navegador abre automaticamente em `http://127.0.0.1:8766`.

Depois disso, `/dashboard` reabre o painel a qualquer momento.

> Se você **instalou pelo marketplace** em vez de clonar o repositório, os arquivos não estão na sua pasta de projetos: o Claude Code copia o plugin para `~/.claude/plugins/cache/`. Os comandos resolvem isso sozinhos via `${CLAUDE_PLUGIN_ROOT}`, então prefira o `/setup` a procurar os arquivos na mão.

O único requisito é Python 3 instalado. O servidor usa somente a biblioteca padrão; não é necessário instalar pacotes com `pip`.

### Onde ficam os dados

Dois arquivos ficam ao lado de `dashboard-server.py`:

- **`projetos-data.json`** — projetos, componentes, reviews e checklists. Criado **quando o primeiro registro é salvo**; antes disso a tela usa uma estrutura vazia em memória, por isso não há arquivo ao abrir o dashboard pela primeira vez.
- **`dashboard-config.json`** — seu perfil (`devLevel`, `projectsRoot`, plataforma e objetivo padrão) e as preferências de scan. Escrito pelo `/setup`.

Para fazer backup, copie os dois. Para reiniciar o Project Hub, feche o servidor e exclua `projetos-data.json` — isso apaga permanentemente os registros do painel, mas não altera seus projetos de código. Excluir `dashboard-config.json` faz o `/setup` rodar o onboarding do zero.

Ambos estão no `.gitignore`: o `dashboard-config.json` também guarda `githubUsername` e `githubToken` e nunca deve ir para o repositório.

## Estrutura do pacote

```text
plugin-react-dev-toolkit/            # raiz = plugin E marketplace
├── .claude-plugin/
│   ├── plugin.json                  # Manifesto do Claude Code
│   └── marketplace.json             # Catálogo do marketplace (Claude Code / Desktop)
├── .codex-plugin/
│   └── plugin.json                  # Manifesto do Codex
├── .agents/plugins/
│   └── marketplace.json             # Marketplace padrão do Codex
├── commands/                        # Comandos de fluxo de trabalho (skills invocáveis por /)
├── skills/react-dev/                # 1 skill + references/
├── scripts/
│   ├── bump-version.py              # sincroniza a versão nos 3 manifestos
│   ├── validate-plugin.py           # checagens de estrutura (roda no CI)
│   ├── atualizar-plugin.ps1         # atualiza Claude + Codex (Windows)
│   └── atualizar-plugin.sh          # atualiza Claude + Codex (macOS/Linux)
├── .github/workflows/
│   └── bump-version.yml             # bump, validação e tag no push da main
├── manual.html                      # Manual visual de consulta rápida
├── LICENSE
└── README.md
```

Regra estrutural da Anthropic: **somente `plugin.json` e `marketplace.json` ficam dentro de `.claude-plugin/`**. `commands/`, `skills/`, `agents/` e `hooks/` precisam estar na raiz do plugin.

## Princípios de mentoria

O plugin atua como parceiro de desenvolvimento, não apenas como gerador de código. Para ideias vagas, primeiro ajuda a definir público, objetivo, MVP, riscos e viabilidade. Para implementação, trabalha de maneira incremental e explica decisões de acordo com o nível do desenvolvedor.

Em cada review, a análise considera: tipagem, tratamento de erro, estados de carregamento, acessibilidade, nomes, separação de responsabilidades, segurança, re-renderizações, cache, tamanho de bundle e cobertura de testes.

## Manual

Abra `manual.html` no navegador para uma visão rápida dos sete comandos e do fluxo recomendado. No topo há um alternador **Claude Code / Codex**: ele reescreve todos os comandos da página com ou sem o prefixo do namespace, então o mesmo arquivo serve para os dois ecossistemas. O manual e este README acompanham a versão do plugin e podem ser mantidos junto à sua pasta de projetos.

<a id="o-que-mudou-na-v151"></a>
<a id="o-que-mudou-na-v1.5.2"></a>
<a id="o-que-mudou-na-v1.5.3"></a>
## O que mudou na v1.5.3

- **Commit:** fix: corrigir workflow de bump automatico
- **Automação de changelog.** `scripts/bump-version.py` agora cria esta seção automaticamente no `README.md` durante o bump de versão.

## O que mudou na v1.5.2

- **Commit:** correção de script workflow bump-version.yml
- **Automação de changelog.** `scripts/bump-version.py` agora cria esta seção automaticamente no `README.md` durante o bump de versão.

## O que mudou na v1.5.1

- **Release v1.5.1.** Commit `chore(release): v1.5.1`.
- **Automação de changelog.** `scripts/bump-version.py` agora insere automaticamente esta seção `O que mudou na vX.Y.Z` no `README.md` sempre que a versão do plugin é bumpada.

<a id="o-que-mudou-na-v150"></a>
## O que mudou na v1.5.0

- **Novo comando `/auditar-seguranca`.** Auditoria de segurança dedicada para React/Next/Expo, o antídoto para as brechas típicas de "vibe coding". Procura segredos vazados no bundle do cliente, dependências vulneráveis (`npm audit`), XSS, injeção, autenticação/autorização frágil e exposição de dados; classifica por severidade (Crítico/Alto/Médio/Baixo) e corrige com aprovação, preservando comportamento. Ao achar um segredo já commitado, orienta a **revogar e rotacionar** a credencial — não só apagar do arquivo. Calibrado por `devLevel` e registrado no Project Hub como índice de postura de segurança.
- **Nova referência `references/security-review.md`.** Modelo de ameaças e checklist de segurança completo (segredos, deps, XSS, injeção, auth, Server Actions/route handlers do Next, especificidades de Expo, exposição de dados e transporte). Entra na tabela do `SKILL.md`.
- **`/review` com passada de segurança embutida.** O code review de rotina agora sempre inclui uma checagem de segurança de primeira linha e aponta para `/auditar-seguranca` quando o caso pede profundidade. As dimensões de performance e casos de borda também foram detalhadas.

<a id="o-que-mudou-na-v140"></a>
## O que mudou na v1.4.0

- **Novo comando `/analisar-projeto-gsd`.** Analisa projetos construídos com o **framework GSD** (Get Stuff Done). Detecta a pasta `.planning/`, lê os artefatos de especificação (`PROJECT.md`, `REQUIREMENTS.md`, `ROADMAP.md`, `STATE.md` e os `PLAN.md`/`SUMMARY.md` de cada fase) e cruza a intenção documentada com o código React/Next/Expo real. Separa os achados em **deriva de spec** e **qualidade técnica**, corrige divergências mediante aprovação (preservando comportamento) e registra tudo no Project Hub. Calibrado pelo `devLevel`, como os demais comandos.
- **Nova referência `references/gsd-analyzer.md`.** Documenta o mapa completo dos artefatos do GSD e a metodologia de análise; entra na tabela do `SKILL.md` e é resolvida por `${CLAUDE_PLUGIN_ROOT}`.

<a id="o-que-mudou-na-v11312"></a>
## O que mudou na v1.3.12

- **Novo comando `/gerar-midia`.** Documentado no README como comando do plugin para gerar imagens hero, previews sociais e vídeos curtos de demonstração usando o MCP da Higgsfield.
- **README atualizado.** Inclui a seção de instalação do Codex CLI e deixa claro que o Codex usa marketplace separado do Claude Code.
- **Sincronização de versão estendida.** `scripts/bump-version.py` agora atualiza também `README.md` e `manual.html`, e o workflow de bump comita esses arquivos junto com os manifestos.

## O que mudou na v1.3.2

- **Publicação automática.** Workflow `bump-version.yml` que, a cada push na `main`, bumpa o patch e sincroniza a versão nos quatro lugares dos três manifestos, valida e cria a tag. É o `version` que faz um commit chegar aos usuários, então sem o bump o push não propagava.
- **`scripts/validate-plugin.py`** — as checagens de estrutura viraram um script do repo que roda no CI. Cobre o que o validador oficial não vê: coerência entre os manifestos do Claude e do Codex, e o menu de slash commands resultante (pega a regressão de skill aparecendo como comando).
- **`scripts/atualizar-plugin.ps1` / `.sh`** — atualizam Claude Code e Codex numa tacada, com `--limpar-cache` para quando algo fica preso.

## O que mudou na v1.3.1

- **Skills fora do menu `/`.** As seis skills de `skills/` ganharam `user-invocable: false`. No Claude Code, todo `SKILL.md` também vira um slash command por padrão, então o plugin expunha 13 entradas no menu — os 7 comandos reais mais as 6 skills. Era o que fazia `/deploy` e `/deploy-advisor-extension` aparecerem lado a lado como se fossem dois comandos de deploy. As skills continuam sendo acionadas pelo modelo normalmente; `user-invocable` só controla a visibilidade no menu.
- **`/deploy` agora é exclusivo do usuário.** `commands/deploy.md` ganhou `disable-model-invocation: true`. Publicar em produção não é uma decisão que o modelo deva tomar sozinho porque o código "parece pronto". O fluxo guiado continua funcionando: a skill `deploy-advisor-extension` segue model-invoked, então falar de deploy na conversa ainda traz o especialista — o que exige sua ação é o comando que publica.

## O que mudou na v1.3.0

- **Compatibilidade com o marketplace do Claude Code.** Novo `.claude-plugin/marketplace.json` com `source: "./"`, habilitando `/plugin marketplace add` por `owner/repo`, URL git ou URL do JSON — e, com isso, a instalação pelo navegador de plugins do Claude Desktop.
- **Plugin renomeado** de `plugin-react-dev` para `plugin-react-dev-toolkit` nos três manifestos, com um mapa `renames` que migra instalações antigas automaticamente.
- **Manifestos completos**: `displayName`, `homepage`, `repository`, `license` e `keywords`, além da licença MIT no repositório.
- **Correções que impediam o carregamento no Claude Code**: `commands/deploy.md` e `skills/deploy-advisor-extension/SKILL.md` estavam sem frontmatter YAML — sem a `description`, a skill de deploy nunca era acionada.
- **`${CLAUDE_PLUGIN_ROOT}` nas referências de arquivo**, necessário porque plugins instalados são copiados para `~/.claude/plugins/cache/` e caminhos relativos não resolvem de lá.
- **`manual.html` atualizado** com `/arquitetura` e `/deploy`, tabela de referência, o fluxo de deploy em seis passos e o alternador de prefixo.

## Licença

MIT — veja [LICENSE](LICENSE).
