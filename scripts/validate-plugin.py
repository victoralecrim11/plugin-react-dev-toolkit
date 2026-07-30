#!/usr/bin/env python3
"""Valida a estrutura do plugin antes de publicar.

Complementa `claude plugin validate .` com checagens que a ferramenta oficial
nao faz: coerencia entre os manifestos do Claude e do Codex, o menu de slash
commands resultante, e residuos de conteudo.

Uso:
    python scripts/validate-plugin.py

Sai com codigo 1 se houver erro. Warnings nao falham.
"""
import glob
import io
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)

errs, warns, oks = [], [], []
E, W, O = errs.append, warns.append, oks.append

KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
RESERVED = {
    "claude-code-marketplace", "claude-code-plugins", "claude-plugins-official",
    "claude-plugins-community", "claude-community", "anthropic-marketplace",
    "anthropic-plugins", "agent-skills", "anthropic-agent-skills",
    "knowledge-work-plugins", "life-sciences", "claude-for-legal",
    "claude-for-financial-services", "financial-services-plugins",
    "first-party-plugins", "healthcare",
}


def load(rel):
    try:
        return json.loads(Path(rel).read_text(encoding="utf-8"))
    except FileNotFoundError:
        E(f"{rel}: nao encontrado")
    except json.JSONDecodeError as exc:
        E(f"{rel}: JSON invalido - {exc}")
    return None


def frontmatter(path):
    """Devolve (dict, erro). Nao usa PyYAML: o CI nao deve precisar de deps."""
    text = Path(path).read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None, "sem frontmatter YAML"
    end = text.find("\n---", 4)
    if end == -1:
        return None, "frontmatter nao fechado"
    data = {}
    for line in text[4:end].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            return None, f"linha sem ':' no frontmatter: {line!r}"
        k, v = line.split(":", 1)
        v = v.strip()
        if v.lower() in ("true", "yes", "on", "1"):
            v = True
        elif v.lower() in ("false", "no", "off", "0"):
            v = False
        data[k.strip()] = v
    return data, None


# ---------- manifestos ----------
pj = load(".claude-plugin/plugin.json")
mp = load(".claude-plugin/marketplace.json")
cx = load(".codex-plugin/plugin.json")
ag = load(".agents/plugins/marketplace.json")

if not all(x is not None for x in (pj, mp, cx, ag)):
    print("\n".join("  ERRO  " + e for e in errs))
    sys.exit(1)

entry = (mp.get("plugins") or [{}])[0]

names = {
    ".claude-plugin/plugin.json": pj.get("name"),
    ".claude-plugin/marketplace.json plugins[0]": entry.get("name"),
    ".codex-plugin/plugin.json": cx.get("name"),
    ".agents/plugins/marketplace.json plugins[0]": (ag.get("plugins") or [{}])[0].get("name"),
}
if len(set(names.values())) == 1:
    O(f"nome consistente nos 4 manifestos: {pj['name']}")
else:
    E(f"nomes divergentes entre manifestos: {names}")

if not KEBAB.match(pj.get("name") or ""):
    E(f"plugin name nao e kebab-case: {pj.get('name')}")

versions = {pj.get("version"), mp.get("version"), entry.get("version"), cx.get("version")}
if len(versions) == 1 and None not in versions:
    O(f"versao consistente: {pj['version']}")
else:
    E(f"versoes divergentes (o bump nao sincronizou tudo): {versions}")

if mp.get("name") in RESERVED:
    E(f"marketplace name reservado pela Anthropic: {mp['name']}")
elif re.search(r"anthropic|official.*claude", mp.get("name", ""), re.I):
    E("marketplace name pode ser bloqueado por impersonar fonte oficial")
else:
    O(f"marketplace name ok: {mp.get('name')}")

if not (isinstance(mp.get("owner"), dict) and mp["owner"].get("name")):
    E("marketplace.json: owner.name e obrigatorio")
if not mp.get("description"):
    W("marketplace.json sem description")

src = entry.get("source")
if isinstance(src, str):
    if ".." in src:
        E("plugins[0].source contem '..' (path traversal)")
    elif not (src.startswith("./") or src == "."):
        E("plugins[0].source relativo deve comecar com './'")
    else:
        O(f'plugins[0].source = "{src}"')
elif isinstance(src, dict):
    if src.get("source") not in ("github", "url", "git-subdir", "npm"):
        E(f"plugins[0].source.source invalido: {src.get('source')}")

for key in ("skills", "commands", "agents"):
    for p in entry.get(key, []) or []:
        if not Path(p).exists():
            E(f"plugins[0].{key}: caminho inexistente {p}")

# renames deve terminar em null ou em plugin listado
listed = {p.get("name") for p in mp.get("plugins", [])}
ren = mp.get("renames") or {}
for old, new in ren.items():
    seen, cur = {old}, new
    while isinstance(cur, str):
        if cur in seen:
            E(f"renames: ciclo em '{old}'")
            break
        if cur in listed:
            O(f"renames: {old} -> {cur}")
            break
        seen.add(cur)
        cur = ren.get(cur, "__missing__")
        if cur == "__missing__":
            E(f"renames: cadeia de '{old}' nao termina em null nem em plugin listado")
            break

# ---------- estrutura ----------
for d in ("commands", "skills", "agents", "hooks"):
    if Path(".claude-plugin", d).is_dir():
        E(f".claude-plugin/{d}/ esta na pasta errada: deve ficar na raiz do plugin")
extra = [f for f in os.listdir(".claude-plugin") if f not in ("plugin.json", "marketplace.json")]
if extra:
    W(f".claude-plugin/ com arquivos extras: {extra}")
else:
    O(".claude-plugin/ contem apenas os manifestos")

# ---------- frontmatter e menu de slash commands ----------
menu, hidden, user_only = [], [], []
cmd_files = sorted(glob.glob("commands/*.md"))
skill_files = sorted(glob.glob("skills/*/SKILL.md"))

for f in cmd_files + skill_files:
    data, err = frontmatter(f)
    if err:
        E(f"{f}: {err}")
        continue
    if not data.get("description"):
        E(f"{f}: frontmatter sem description")
    is_skill = f.endswith("SKILL.md")
    name = data.get("name") or (
        os.path.basename(os.path.dirname(f)) if is_skill else os.path.basename(f)[:-3]
    )
    (menu if data.get("user-invocable", True) else hidden).append(name)
    if data.get("disable-model-invocation"):
        user_only.append(name)

O(f"frontmatter valido em {len(cmd_files) + len(skill_files)} arquivos")

expected_menu = {os.path.basename(f)[:-3] for f in cmd_files}
if set(menu) == expected_menu:
    O(f"menu '/' tem exatamente os {len(expected_menu)} comandos de commands/")
else:
    extra_in_menu = sorted(set(menu) - expected_menu)
    if extra_in_menu:
        E(
            "estes itens aparecem no menu '/' sem serem comandos: "
            f"{extra_in_menu}. Toda SKILL.md tambem vira slash command; "
            "use 'user-invocable: false' nas skills que sao base de conhecimento."
        )
    if expected_menu - set(menu):
        E(f"comandos fora do menu: {sorted(expected_menu - set(menu))}")

ambiguous = sorted({f"{a} / {b}" for a in menu for b in menu if a != b and b.startswith(a)})
if ambiguous:
    W(f"nomes no menu em que um e prefixo do outro (parecem duplicados): {ambiguous}")
else:
    O("nenhum nome do menu e prefixo de outro")

if "deploy" in expected_menu and "deploy" not in user_only:
    W("commands/deploy.md sem 'disable-model-invocation: true': o modelo pode publicar sozinho")
elif "deploy" in user_only:
    O("/deploy exige acao do usuario (disable-model-invocation)")

adv, err = frontmatter("skills/deploy-advisor-extension/SKILL.md") if Path(
    "skills/deploy-advisor-extension/SKILL.md"
).exists() else (None, "ausente")
if adv and adv.get("disable-model-invocation"):
    E("deploy-advisor-extension bloqueado para o modelo: o fluxo guiado do /deploy quebraria")

# ---------- higiene ----------
junk = 0
for f in glob.glob("**/*.md", recursive=True):
    n = len(re.findall(r"\[cite:\s*\d+\]", Path(f).read_text(encoding="utf-8")))
    if n:
        E(f"{f}: {n} marcador(es) [cite: N] residuais")
        junk += n
if not junk:
    O("nenhum marcador [cite: N] residual")

bytecode = glob.glob("**/__pycache__", recursive=True) + glob.glob("**/*.pyc", recursive=True)
if bytecode:
    E(f"bytecode versionado: {bytecode}")
else:
    O("sem __pycache__/*.pyc")

# caminhos que quebram quando instalado por marketplace
bad_paths = []
for f in cmd_files + skill_files:
    text = Path(f).read_text(encoding="utf-8")
    for m in re.finditer(r"`(?!\$\{CLAUDE_PLUGIN_ROOT\})[^`\n]*references/[^`\n]*`", text):
        bad_paths.append(f"{f}: {m.group(0)}")
if bad_paths:
    W(
        "caminhos para references/ sem ${CLAUDE_PLUGIN_ROOT} (plugins instalados "
        f"sao copiados para o cache): {bad_paths}"
    )
else:
    O("referencias de arquivo usam ${CLAUDE_PLUGIN_ROOT}")

# ---------- saida ----------
for o in oks:
    print(f"  OK    {o}")
if warns:
    print()
    for w in warns:
        print(f"  WARN  {w}")
if errs:
    print()
    for e in errs:
        print(f"  ERRO  {e}")
print(f"\n{len(errs)} erro(s), {len(warns)} warning(s)")
sys.exit(1 if errs else 0)
