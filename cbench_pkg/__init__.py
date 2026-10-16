"""cbench package: compiler benchmark suite.

Public API:
    from cbench_pkg.cli import main
    from cbench_pkg.types import LangSupport, register_language, LANGUAGES, Op
    from cbench_pkg.generation import generate_test_program_source, generate_test_program_file
    from cbench_pkg.compiler import benchmark_compiler_op
    from cbench_pkg.reporting import markdown_table
"""

from .cli import main
from .types import (
    Lang,
    Exec,
    FileExt,
    TypeName,
    Op,
    ValuesMode,
    ResultKey,
    RawCol,
    LangSupport,
    Results,
    register_language,
    lang_support,
    default_exes,
    build_lang_aliases,
    LANGUAGES,
    VERSIONS,
    DUR_COLS,
    DEFAULT_PROGRAM_NAME,
    DEFAULT_OPERATIONS,
    SUPPORTED_OPERATIONS,
)
from .version import get_compiler_version, resolve_compiler_path, find_compiler_versions

__all__ = [
    "main",
    "Lang",
    "Exec",
    "FileExt",
    "TypeName",
    "Op",
    "ValuesMode",
    "ResultKey",
    "RawCol",
    "LangSupport",
    "Results",
    "register_language",
    "lang_support",
    "default_exes",
    "build_lang_aliases",
    "LANGUAGES",
    "VERSIONS",
    "DUR_COLS",
    "DEFAULT_PROGRAM_NAME",
    "DEFAULT_OPERATIONS",
    "SUPPORTED_OPERATIONS",
    "get_compiler_version",
    "resolve_compiler_path",
    "find_compiler_versions",
]
