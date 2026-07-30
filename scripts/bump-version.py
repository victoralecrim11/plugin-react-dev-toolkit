#!/usr/bin/env python3
"""Sincroniza a versao do plugin nos manifestos do Claude Code e do Codex.

Uso:
    python scripts/bump-version.py            # bump do patch
    python scripts/bump-version.py --minor
    python scripts/bump-version.py --major
    python scripts/bump-version.py --set 2.0.0
    python scripts/bump-version.py --check    # so imprime, nao escreve

Edita apenas a string da versao, preservando a formatacao dos JSONs
(nao reserializa: isso evitaria diffs de formatacao desnecessarios).
"""
import argparse
import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# arquivo -> quantas ocorrencias de "version" devem existir
TARGETS = {
    ".claude-plugin/plugin.json": 1,
    ".claude-plugin/marketplace.json": 2,   # topo + entrada do plugin
    ".codex-plugin/plugin.json": 1,
}

VERSION_RE = re.compile(r'("version"\s*:\s*")(\d+\.\d+\.\d+)(")')


def read_current():
    p = ROOT / ".claude-plugin/plugin.json"
    v = json.loads(p.read_text(encoding="utf-8")).get("version")
    if not v:
        sys.exit("erro: .claude-plugin/plugin.json nao tem campo version")
    return v


def bump(v, part):
    major, minor, patch = (int(x) for x in v.split("."))
    if part == "major":
        return f"{major + 1}.0.0"
    if part == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--major", action="store_true")
    g.add_argument("--minor", action="store_true")
    g.add_argument("--patch", action="store_true")
    g.add_argument("--set", dest="explicit", metavar="X.Y.Z")
    ap.add_argument("--check", action="store_true", help="nao escreve, so valida")
    args = ap.parse_args()

    current = read_current()
    if args.explicit:
        if not re.fullmatch(r"\d+\.\d+\.\d+", args.explicit):
            sys.exit(f"erro: '{args.explicit}' nao e semver X.Y.Z")
        new = args.explicit
    else:
        part = "major" if args.major else "minor" if args.minor else "patch"
        new = bump(current, part)

    if args.check:
        print(f"atual={current}")
        print(f"proxima={new}")

    problems, written = [], []
    for rel, expected in TARGETS.items():
        path = ROOT / rel
        if not path.exists():
            problems.append(f"{rel}: arquivo nao encontrado")
            continue
        text = path.read_text(encoding="utf-8")
        found = len(VERSION_RE.findall(text))
        if found != expected:
            problems.append(f"{rel}: esperava {expected} campo(s) version, achei {found}")
            continue
        if args.check:
            written.append(f"  {rel}: {found} ocorrencia(s) ok")
            continue
        new_text = VERSION_RE.sub(lambda m: m.group(1) + new + m.group(3), text)
        # falha alto se o JSON quebrar
        try:
            json.loads(new_text)
        except json.JSONDecodeError as exc:
            problems.append(f"{rel}: substituicao geraria JSON invalido ({exc})")
            continue
        if new_text != text:
            path.write_text(new_text, encoding="utf-8", newline="\n")
        written.append(f"  {rel}: {current} -> {new}")

    if problems:
        print("FALHOU:", file=sys.stderr)
        for p in problems:
            print("  " + p, file=sys.stderr)
        sys.exit(1)

    print("\n".join(written))
    if not args.check:
        # confere que as 4 ocorrencias ficaram iguais
        seen = set()
        for rel in TARGETS:
            for m in VERSION_RE.finditer((ROOT / rel).read_text(encoding="utf-8")):
                seen.add(m.group(2))
        if seen != {new}:
            sys.exit(f"erro: versoes divergentes apos o bump: {sorted(seen)}")
        print(f"\nversao sincronizada em {sum(TARGETS.values())} lugares: {new}")
        print(f"::set-version::{new}")


if __name__ == "__main__":
    main()
