"""
Core types and the language registry for the cbench compiler benchmark.

This module defines the shared data model (`Op`, `ValuesMode`, `LangSupport`,
the `LANGUAGES` registry, etc.) that the rest of the engine talks to. Nothing
outside a language block needs to change to add a new language: register a
`LangSupport` in `cbench/lang/<name>.py` and the generic engine picks it up.
"""

import argparse
import os
import random
from datetime import datetime
from enum import Enum
from typing import Callable, NamedTuple, NewType, override
from collections.abc import Callable
from dataclasses import dataclass, field

# --- identity / toolchain ---
Lang = NewType("Lang", str)
Exec = NewType("Exec", str)
FileExt = NewType("FileExt", str)
TypeName = NewType("TypeName", str)


class Op(str, Enum):
    """Supported compiler benchmark operations."""
    AST_CHECK = "ast-check"
    CHECK = "check"
    COMPILE = "compile"
    BUILD = "build"
    RUN = "run"

    @override
    def __str__(self) -> str:
        return self.value


class ValuesMode(str, Enum):
    """Output display mode for metrics."""
    ABSOLUTE = "absolute"
    RELATIVE = "relative"
    BOTH = "both"

    @override
    def __str__(self) -> str:
        return self.value


class ResultKey(NamedTuple):
    """Composite lookup key for benchmark results."""
    lang: Lang
    templated: bool
    cexec: Exec


class RawCol(str, Enum):
    LANG = "Language"
    TEMPLATED = "Templated"
    AST_CHECK_DUR = "AST-Check Duration"
    CHECK_DUR = "Check Duration"
    COMPILE_DUR = "Compile Duration"
    BUILD_DUR = "Build Duration"
    RUN_DUR = "Run Duration"
    CHECK_RSS = "Check RSS"
    BUILD_RSS = "Build RSS"
    OUTPUT_SIZE = "Output Size"
    CEXE_VERSION = "Compiler Version"
    CEXE_PATH = "Compiler Path"


DUR_COLS = {
    RawCol.AST_CHECK_DUR,
    RawCol.CHECK_DUR,
    RawCol.COMPILE_DUR,
    RawCol.BUILD_DUR,
    RawCol.RUN_DUR,
}

Results = dict[ResultKey, dict[RawCol, object]]

DEFAULT_PROGRAM_NAME = "main"
DEFAULT_FUNCTION_COUNT = 200
DEFAULT_FUNCTION_DEPTH = 200
DEFAULT_RUN_COUNT = 10
DEFAULT_SAMPLE_RATE = 100
DEFAULT_TIMEOUT = 60.0

ADAPTIVE_FAST_DUR_THRESHOLD = 1.0
ADAPTIVE_FAST_RUN_COUNT = 3
ADAPTIVE_SLOW_DUR_THRESHOLD = 3.0
ADAPTIVE_SLOW_RUN_COUNT = 2

HOMOGENEOUS_CPU_RESERVE = 2
PROGRESS_POLL_INTERVAL_SEC = 0.2
MONITOR_JOIN_TIMEOUT_SEC = 1.0
TEMP_DIR_BASE = "/tmp"
TEMP_DIR_PREFIX = "generated_"

RAND_POOL_SIZE = 4096
RAND_POOL_MASK = RAND_POOL_SIZE - 1
RAND_INT_MAX = 100_000

DEFAULT_OPERATIONS: list[Op] = [
    Op.CHECK,
    Op.COMPILE,
    Op.BUILD,
    Op.RUN,
]

SUPPORTED_OPERATIONS: list[Op] = [
    Op.AST_CHECK,
    *DEFAULT_OPERATIONS,
]

ROOT_PATH = None
MAIN_PID = os.getpid()
_worker_active_tasks = None
_worker_status_len = None

RANGE = range(5, 20)
VERSIONS = [''] + [f"-{i}" for i in RANGE]

RANDOMIZE_FLAG = True

if RANDOMIZE_FLAG:
    random.seed(str(datetime.now()))

RAND_STR_POOL = [str(random.randint(0, RAND_INT_MAX)) for _ in range(RAND_POOL_SIZE)]


def function_name(typ: str, findex: int, fheight: int | None = None) -> str:
    """Fast f-string based function name formatter."""
    if fheight is not None:
        return f"add_{typ}_n{findex}_h{fheight}"
    return f"add_{typ}_n{findex}"


class VersionSpec(NamedTuple):
    """How to obtain a compiler version for executables whose basename starts with `prefixes`.

    fixed: if set, no process is run and this string is the version.
    args:  arguments passed to the compiler (default: ['--version']).
    parse: (output, default) -> version | None. None falls back to the generic parser.
    """
    prefixes: tuple[str, ...]
    args: list[str] | None = None
    parse: Callable[[str, str], str | None] | None = None
    fixed: str | None = None


def _no_text(*_args) -> str:
    return ''


def plain_call(findex: int, typ: str, templated: bool) -> str:
    """Default call statement: `<T>_sum += add_<T>_n<i>(<i>)` (indentation included)."""
    return f"    {typ}_sum += {function_name(typ, findex)}({findex})"


def _default_program_dir(dir_path: str, templated: bool, run_ix: int) -> str:
    return dir_path


def _default_source_filename(program_name: str, templated: bool, run_ix: int, ext: str) -> str:
    return f"{program_name}{'_t' if templated else ''}_{run_ix}.{ext}"


def _defs_then_header(write_header: Callable[[], None], write_defs: Callable[[], None]) -> None:
    write_defs()
    write_header()


def _always_native(cexe: str) -> bool:
    return True


def _never_native(cexe: str) -> bool:
    return False


def _no_limits(args: argparse.Namespace) -> list[str]:
    return []


def _default_leaf(typ: str, templated: bool, c: str) -> str:
    return f"x + {c}"


def _default_chain(typ: str, templated: bool, prev: str, c: str) -> str:
    return f"x + {prev}(x) + {c}"


def make_func_emitter(define: Callable[[str, str, str, bool], str],
                      leaf: Callable[[str, bool, str], str] = _default_leaf,
                      chain: Callable[[str, bool, str, str], str] = _default_chain):
    """Build a `func_emitter` for a LangSupport.

    define(fname, typ, expr, templated) -> text of one function definition
    leaf(typ, templated, c)             -> expression of the innermost function (height 0)
    chain(typ, templated, prev, c)      -> expression calling the previous-height function
    """
    def factory(typ: str, templated: bool, depth: int):
        def emit(findex: int, fheight: int, nconst: str) -> str:
            if fheight == 0:
                expr = leaf(typ, templated, nconst)
            else:
                prev = function_name(typ, findex, fheight - 1)
                expr = chain(typ, templated, prev, nconst)
            fname = function_name(typ, findex, None if fheight == depth - 1 else fheight)
            return define(fname, typ, expr, templated)
        return emit
    return factory


def lisp_let_middle(types: list[str]) -> str:
    """`(let ((T_sum 0)) ` opener shared by Scheme-family languages."""
    bindings = ' '.join(f'({typ}_sum 0)' for typ in types)
    return f'  (let ({bindings})\n'


@dataclass
class LangSupport:
    """Everything the engine needs to know about one language."""
    # --- identity / toolchain ---
    name: Lang
    exes: list[Exec]
    extension: FileExt
    int_type: TypeName
    runners: list[Callable]                    # (results, code_paths, args, op, templated) -> None
    ops: tuple[str, ...]
    templated_variants: tuple[bool, ...] = (False,)
    # --- reporting ---
    tier: int = 2                              # 1 minimalist, 2 AOT systems, 3 managed/VM/scripting
    exe_tiers: dict[str, int] = field(default_factory=dict)   # basename prefix -> tier override
    aliases: tuple[str, ...] = ()              # extra --languages spellings (lowercase)
    # --- toolchain behaviour ---
    out_binary: str = DEFAULT_PROGRAM_NAME
    native_output: Callable[[str], bool] = _always_native      # cexe -> does build emit machine code?
    versions: list[VersionSpec] = field(default_factory=list)
    limit_args: Callable[[argparse.Namespace], list[str]] = _no_limits  # mutates args, returns warnings
    build_cmd: Callable[[str, list, list, str], list] | None = None    # (cexe, flags, out, src) -> argv
    # --- source generation ---
    func_emitter: Callable = None              # (typ, templated, depth) -> emit(findex, fheight, nconst)
    main_header: Callable[[list[str], bool], str] = _no_text
    postfix: Callable[[list[str]], str] = _no_text
    prefix: Callable[[str, bool], str] = _no_text              # (program_name, templated)
    var_decl: Callable[[str, bool], str] = _no_text            # (typ, templated)
    main_middle: Callable[[list[str]], str] = _no_text         # (types)
    call: Callable[[int, str, bool], str] = plain_call         # (findex, typ, templated) -> line w/o terminator
    call_terminator: str = ';'
    # --- per-language file layout quirks (passed to generate_test_program_file) ---
    program_dir: Callable[[str, bool, int], str] = _default_program_dir
    source_filename: Callable[[str, bool, int, str], str] = _default_source_filename
    order_sections: Callable[[Callable[[], None], Callable[[], None]], None] = _defs_then_header


LANGUAGES: dict[Lang, LangSupport] = {}
_BY_LOWER: dict[str, LangSupport] = {}
VERSION_SPECS: list[VersionSpec] = []


def register_language(spec: LangSupport) -> LangSupport:
    if spec.name in LANGUAGES:
        raise ValueError(f"Language {spec.name} registered twice")
    LANGUAGES[spec.name] = spec
    _BY_LOWER[spec.name.lower()] = spec
    VERSION_SPECS.extend(spec.versions)
    return spec


def lang_support(lang: str) -> LangSupport:
    try:
        return _BY_LOWER[str(lang).lower()]
    except KeyError:
        raise NotImplementedError(f"Missing language configuration for '{lang}'") from None


def default_exes(lang: str) -> list[Exec]:
    return lang_support(lang).exes


def build_lang_aliases() -> dict[str, Lang]:
    aliases: dict[str, Lang] = {}
    for spec in LANGUAGES.values():
        aliases[spec.name.lower()] = spec.name
        for a in spec.aliases:
            aliases[a.lower()] = spec.name
    return aliases
