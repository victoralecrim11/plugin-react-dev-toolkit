---
name: nextjs-extension
description: Particularidades modernas de Next.js App Router, Server Components, Server Actions e SSR.
user-invocable: false
---
# Next.js Extension

Use junto de `react-core` em Next.js. Prefira App Router e TypeScript.

- Server Components são o padrão para leitura e composição que não exigem interatividade; use `"use client"` somente em fronteiras que usam estado, eventos ou APIs do navegador.
- Faça carregamento de dados no servidor quando isso reduzir JavaScript enviado e beneficiar SEO; mantenha segredos e acesso privilegiado no servidor.
- Use Server Actions para mutações de formulários simples e valide entrada no servidor. Para APIs públicas, integrações externas ou clientes não-Next, crie Route Handlers.
- Modele loading, error e not-found por rota. Documente cache/revalidação antes de otimizar.

Explique a divisão servidor/cliente e os trade-offs de SSR, SSG e renderização dinâmica em cada decisão.
