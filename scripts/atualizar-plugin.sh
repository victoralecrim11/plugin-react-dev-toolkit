#!/usr/bin/env bash
# Atualiza o React Dev Hub no Claude Code e no Codex de uma vez.
#
# Rode depois de um push para trazer a versao nova para as duas plataformas.
# Nao instala o plugin do zero -- para isso, veja o README.
#
# Nenhuma das duas recarrega uma sessao aberta: no Claude Code use
# /reload-plugins, no Codex reinicie o app.
#
# Uso:
#   ./scripts/atualizar-plugin.sh
#   ./scripts/atualizar-plugin.sh --limpar-cache

set -uo pipefail

PLUGIN="${PLUGIN:-plugin-react-dev-toolkit}"
MARKETPLACE="${MARKETPLACE:-react-dev-marketplace}"
LIMPAR_CACHE=0
falhas=()

for arg in "$@"; do
  case "$arg" in
    --limpar-cache) LIMPAR_CACHE=1 ;;
    -h|--help) sed -n '2,13p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "argumento desconhecido: $arg" >&2; exit 2 ;;
  esac
done

titulo() { printf '\n\033[36m== %s\033[0m\n' "$1"; }
aviso()  { printf '\033[33m  %s\033[0m\n' "$1"; }
ok()     { printf '\033[32m  %s\033[0m\n' "$1"; }

titulo 'Claude Code'
if command -v claude >/dev/null 2>&1; then
  if [ "$LIMPAR_CACHE" -eq 1 ] && [ -d "$HOME/.claude/plugins/cache" ]; then
    rm -rf "$HOME/.claude/plugins/cache"
    aviso 'cache removido: ~/.claude/plugins/cache'
  fi
  # sem nome, atualiza todos os marketplaces configurados
  claude plugin marketplace update "$MARKETPLACE" \
    || falhas+=('claude plugin marketplace update')
  # `plugin update` exige o nome do plugin; nao existe --all
  claude plugin update "${PLUGIN}@${MARKETPLACE}" \
    || falhas+=('claude plugin update')
  ok 'feito. Numa sessao aberta, rode /reload-plugins.'
else
  aviso "CLI 'claude' nao encontrada no PATH -- pulando."
fi

titulo 'Codex'
if command -v codex >/dev/null 2>&1; then
  if [ "$LIMPAR_CACHE" -eq 1 ] && [ -d "$HOME/.codex/plugins/cache" ]; then
    rm -rf "$HOME/.codex/plugins/cache"
    aviso 'cache removido: ~/.codex/plugins/cache'
  fi
  codex plugin marketplace list
  # sem nome, faz upgrade de todos os marketplaces configurados
  codex plugin marketplace upgrade \
    || falhas+=('codex plugin marketplace upgrade')
  ok 'feito. Reinicie o Codex para carregar os arquivos novos.'
else
  aviso "CLI 'codex' nao encontrada no PATH -- pulando."
fi

echo
if [ "${#falhas[@]}" -gt 0 ]; then
  printf '\033[31mFalhou: %s\033[0m\n' "${falhas[*]}"
  exit 1
fi
ok 'Atualizacao concluida.'
