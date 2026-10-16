"""Language support for clojure.

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
    _always_native, _never_native, default_exes, VersionSpec, DEFAULT_PROGRAM_NAME,
)
from ..version import resolve_compiler_path, find_compiler_versions, get_compiler_version
from ..compiler import benchmark_compiler_op, build_compiler_cmd, out_directory, out_binary
from ._shared import clojure_limits as _clojure_limits

def _clojure_parse_version(out: str, default: str) -> str | None:
    m = re.search(r"(?:version\s+)?([0-9]+(?:\.[0-9]+)+)", out, re.IGNORECASE)
    if m:
        return m.group(1)
    return None


def bm_Clojure(results: Results, code_paths: list, args: argparse.Namespace, op: str, templated: bool):
    lang = "Clojure"

    for cexe_name in (args.language_exes.get(lang) or default_exes(lang)):
        cexe = resolve_compiler_path(args, lang, cexe_name)
        if not cexe:
            continue

        if op == "check":
            cexe_flags = ["-J-Dcbench.check=true", "-M"]
        elif op == "build":
            cexe_flags = ["-M"]
        else:
            continue

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
    name=Lang("Clojure"), exes=[Exec("clojure")], extension=FileExt("clj"), int_type=TypeName("long"),
    runners=[bm_Clojure],
    ops=("check", "build"),
    aliases=("clojure", "clj"),
    templated_variants=(False, True),
    tier=3,
    native_output=_never_native,
    versions=[VersionSpec(("clojure"), ["--version"], _clojure_parse_version)],
    limit_args=_clojure_limits,
    func_emitter=make_func_emitter(
        define=lambda fname, typ, expr, t: (
            f"(defn {fname} ^long [^long x]\n  {expr})\n" if t
            else f"(defn {fname} [x]\n  {expr})\n"),
        leaf=lambda typ, t, c: f"(+ x {c})",
        chain=lambda typ, t, prev, c: f"(+ x ({prev} x) {c})",
    ),
    prefix=lambda program_name, t: f"(ns {program_name})\n\n",
    main_header=lambda types, t: "(defn -main [& _args]\n",
    var_decl=lambda typ, t: f"  (let [{typ}_sum (atom 0)]\n",
    call=lambda i, typ, t: f"    (swap! {typ}_sum + ({function_name(typ, i)} {i}))",
    call_terminator="",
    postfix=lambda types: (
        f"    (System/exit (if (== (mod @{types[0]}_sum 256) 42) 1 0))))\n\n"
        "(when-not (= (System/getProperty \"cbench.check\") \"true\")\n"
        "  (-main))\n"
    ),
))
