"""
Compiler version probing.

Discovers compiler executables and extracts version identifiers. Per-compiler
probing is declared via `VersionSpec` (registered by each language block).
"""

import os
import re
import subprocess as sp
from shutil import which

from .types import VersionSpec, VERSIONS, VERSION_SPECS


def _compact_version(ver: str) -> str:
    """Compact git describe outputs and strip packaging noise."""
    clean = ver.split('~')[0].split('ubuntu')[0]
    m = re.match(r"^v?(\d+\.\d+(?:\.\d+)?).*?-\d+-g([0-9a-f]{7})[0-9a-f]*$", clean, re.IGNORECASE)
    if m:
        return f"{m.group(1)}-{m.group(2)}"
    if clean.startswith('v') and len(clean) > 1 and clean[1].isdigit():
        clean = clean[1:]
    return clean


def get_compiler_version(cexe: str, default: str = 'unknown') -> str:
    """Extract a version identifier; per-compiler probing is declared via VersionSpec."""
    base = os.path.basename(cexe)
    spec = next((v for v in VERSION_SPECS if base.startswith(v.prefixes)), None)
    if spec is not None and spec.fixed is not None:
        return spec.fixed
    cmd = [cexe] + (spec.args if spec is not None and spec.args is not None else ['--version'])
    try:
        res = sp.run(cmd, stdout=sp.PIPE, stderr=sp.PIPE)
        out = (res.stdout or res.stderr).decode('utf-8', errors='ignore').strip()
        if spec is not None and spec.parse is not None:
            parsed = spec.parse(out, default)
            if parsed is not None:
                return _compact_version(parsed)
        for part in out.split():
            clean = part.strip(',;:()')
            if clean and (clean[0].isdigit() or (clean.startswith('v') and len(clean) > 1 and clean[1].isdigit())):
                return _compact_version(clean)
    except Exception:
        pass
    return default


def resolve_compiler_path(args, lang: str, cexe_name: str):
    try:
        if args.language_exes[lang] and cexe_name not in args.language_exes[lang]:
            return None
    except KeyError:
        pass
    cexe_path = which(cexe_name, path=args.path)
    return cexe_path


def find_compiler_versions(args, lang: str, base_name: str):
    for v in VERSIONS:
        cexe = resolve_compiler_path(args, lang, f"{base_name}{v}")
        if cexe:
            yield cexe
