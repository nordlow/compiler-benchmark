"""Language support for fsharp.

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
from ._shared import fsharp_limits as _fsharp_limits

def _fsharp_parse_version(out: str, default: str) -> str | None:
    m = re.search(r"version\s+([0-9a-zA-Z.-]+)", out, re.IGNORECASE)
    if m:
        return m.group(1)
    m = re.search(r"F#\s+([0-9a-zA-Z.-]+)", out)
    if m:
        return m.group(1)
    return None


def _dotnet_fsharp_build_cmd(cexe, cexe_flags, out_flags, src_name):
    return [cexe, "fsi"] + cexe_flags + out_flags + [src_name]


def bm_FSharp(results: Results, code_paths: list, args: argparse.Namespace, op: str, templated: bool):
    lang = "F#"
    cexe = resolve_compiler_path(args, lang, "dotnet")
    if not cexe:
        return None

    if op == "check":
        cexe_flags = ["--nologo", "--quiet", "--typecheck-only"]
    elif op in ("build", "run"):
        cexe_flags = ["--nologo", "--quiet", "--exec"]
    else:
        return None

    version = get_compiler_version(cexe)
    benchmark_compiler_op(code_paths,
                          out_flag_and_exe=[],
                          cexe=cexe,
                          exec_cmd=False,
                          cexe_flags=cexe_flags,
                          args=args,
                          op=op,
                          compiler_version=version,
                          lang=lang,
                          templated=templated,
                          results=results)


register_language(LangSupport(
    name=Lang("F#"),
    exes=[Exec("dotnet")],
    extension=FileExt("fsx"),
    int_type=TypeName("int64"),
    runners=[bm_FSharp],
    ops=("check", "build"),
    aliases=("fsharp", "f#", "fsi", "dotnet-fsi"),
    tier=3,
    native_output=_never_native,
    versions=[VersionSpec(("dotnet",), ["fsi", "--version"], _fsharp_parse_version)],
    limit_args=_fsharp_limits,
    build_cmd=_dotnet_fsharp_build_cmd,
    func_emitter=make_func_emitter(
        define=lambda fname, typ, expr, t: f"let {fname} (x: {typ}) : {typ} = {expr}\n",
        leaf=lambda typ, t, c: f"x + {c}L",
        chain=lambda typ, t, prev, c: f"x + {prev}(x) + {c}L",
    ),
    prefix=lambda program_name, t: "open System\n\n",
    main_header=lambda types, t: "let main () =\n",
    var_decl=lambda typ, t: f"    let mutable {typ}_sum: {typ} = 0L\n",
    call=lambda i, typ, t: f"    {typ}_sum <- {typ}_sum + {function_name(typ, i)}({i}L)",
    call_terminator="",
    postfix=lambda types: f"    exit (if {types[0]}_sum = -1L then 1 else 0)\n\nmain ()\n",
))
