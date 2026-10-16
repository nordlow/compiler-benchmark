"""Language support for kotlin.

Self-contained block: runner(s) + register_language call. To add a new language,
drop a new module here and it is picked up automatically by the engine.
"""
import argparse
import copy
import os
import shutil
import tempfile
from shutil import which

from ..types import (
    Lang, Exec, FileExt, TypeName, LangSupport, register_language,
    make_func_emitter, plain_call, function_name, lisp_let_middle,
    _default_leaf, _default_chain, _no_limits, _no_text, _defs_then_header,
    _always_native, _never_native, VersionSpec, DEFAULT_PROGRAM_NAME,
)
from ..version import resolve_compiler_path, find_compiler_versions, get_compiler_version
from ..compiler import benchmark_compiler_op, build_compiler_cmd, out_directory, out_binary

KOTLIN_MAX_TOTAL_FUNCS = 10_000
KOTLIN_CAPPED_DIM = 100


def _kotlin_limits(args: argparse.Namespace) -> list[str]:
    if args.function_count * args.function_depth > KOTLIN_MAX_TOTAL_FUNCS:
        msg = (f"Warning: Capping Kotlin function count/depth from {args.function_count}x{args.function_depth} "
               f"to {KOTLIN_CAPPED_DIM}x{KOTLIN_CAPPED_DIM} due to JVM constant pool and compiler scaling limits")
        args.function_count = KOTLIN_CAPPED_DIM
        args.function_depth = KOTLIN_CAPPED_DIM
        return [msg]
    return []


def _kotlin_parse_version(out: str, default: str) -> str | None:
    m = re.search(r"kotlin(?:c(?:-jvm)?)?\s+(?:version\s+)?([0-9a-zA-Z.-]+)", out, re.IGNORECASE)
    if m:
        return m.group(1)
    return None


def bm_Kotlin(results: Results, code_paths: list, args: argparse.Namespace, op: str, templated: bool):
    lang = "Kotlin"
    cexe = resolve_compiler_path(args, lang, "kotlinc")
    if not cexe:
        return None

    version = get_compiler_version(cexe)
    java_exe = which("java")

    if op == "check":
        with tempfile.TemporaryDirectory() as tmp_dir:
            benchmark_compiler_op(code_paths,
                                  out_flag_and_exe=["-d", tmp_dir],
                                  cexe=cexe,
                                  exec_cmd=False,
                                  cexe_flags=["-nowarn"],
                                  args=args,
                                  op=op,
                                  compiler_version=version,
                                  lang=lang,
                                  templated=templated,
                                  results=results)
    elif op == "build":
        target_jar = out_binary(lang)
        benchmark_compiler_op(code_paths,
                              out_flag_and_exe=["-include-runtime", "-d", target_jar],
                              cexe=cexe,
                              exec_cmd=[java_exe, "-jar"] if java_exe else False,
                              cexe_flags=["-nowarn"],
                              args=args,
                              op=op,
                              compiler_version=version,
                              lang=lang,
                              templated=templated,
                              results=results)
    else:
        return None


register_language(LangSupport(
    name=Lang("Kotlin"), exes=[Exec("kotlinc")], extension=FileExt("kt"), int_type=TypeName("Long"),
    runners=[bm_Kotlin],
    ops=("check", "build"),
    aliases=("kt", "kotlinc"),
    tier=3,
    out_binary=DEFAULT_PROGRAM_NAME + ".jar",
    native_output=_never_native,
    versions=[VersionSpec(("kotlinc",), ["-version"], _kotlin_parse_version)],
    limit_args=_kotlin_limits,
    func_emitter=make_func_emitter(
        define=lambda fname, typ, expr, t: f"fun {fname}(x: {typ}): {typ} = {expr}\n",
        leaf=lambda typ, t, c: f"x + {c}L",
        chain=lambda typ, t, prev, c: f"x + {prev}(x) + {c}L",
    ),
    prefix=lambda program_name, t: "@file:JvmName(\"Main\")\n\n",
    main_header=lambda types, t: "fun main(args: Array<String>) {\n",
    var_decl=lambda typ, t: f"    var {typ.lower()}_sum: {typ} = 0L\n",
    call=lambda i, typ, t: f"    {typ.lower()}_sum += {function_name(typ, i)}({i}L)",
    call_terminator="",
    postfix=lambda types: f"    System.exit(if ({types[0].lower()}_sum == 42L) 1 else 0)\n}}\n",
))
