---
name: dashboard-projetos
description: Mantém o Project Hub local para acompanhar projetos React, componentes, code reviews e checklist arquitetural.
---
# Dashboard de Projetos

Use quando o usuário disser dashboard, projetos, componentes reutilizáveis, reviews, métricas, dívida técnica ou checklist arquitetural. O painel é local, sem banco externo, e usa `projetos-data.json` como fonte da verdade.

## Inicialização

Copie `references/dashboard-server.py`, `dashboard-template.html` e o inicializador adequado para a pasta desejada. Execute o inicializador; o servidor Python padrão abre `http://127.0.0.1:8766`. Não requer pip.

## Dados que comandos devem registrar

- Projeto: nome, caminho, plataforma, status, versão React, stack, nível e notas.
- Componente: nome, projeto, categoria, caminho e descrição de reuso.
- Review: projeto, data, score de manutenibilidade (0–100), resumo e lista de débitos.
- Checklist: itens por nível, marcados quando evidenciados no projeto.

Faça mutações pelos endpoints locais `GET/POST /api/data`, `POST /api/projects`, `POST /api/components`, `POST /api/reviews` e `POST /api/checklists`. O dashboard também permite editar e excluir visualmente. Nunca envie os dados para serviços externos.
