"""Language support for r.

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
from ._shared import r_limits as _r_limits

def _r_parse_version(out: str, default: str) -> str | None:
    m = re.search(r"R\s+version\s+([0-9]+(?:\.[0-9]+)+)", out, re.IGNORECASE)
    if m:
        return m.group(1)
    return None


def bm_R(results: Results, code_paths: list, args: argparse.Namespace, op: str, templated: bool):
    lang = 'R'
    target_rc = out_binary(lang)

    exes = args.language_exes.get(lang) or default_exes(lang)

    for cexe_name in exes:
        cexe = resolve_compiler_path(args, lang, cexe_name)
        if not cexe:
            continue

        if op == 'check':
            # Parse AST without evaluation (syntax / static parse check)
            cexe_flags = [
                '--vanilla', '-q', '-s',
                '-e', 'invisible(suppressWarnings(parse(file = commandArgs(trailingOnly = TRUE)[1])))',
                '--args',
            ]
            out_flag_and_exe = []
            exec_cmd = False
        elif op == 'compile':
            # Compile source into R bytecode (.Rc) using base package 'compiler'
            cexe_flags = [
                '--vanilla', '-q', '-s',
                '-e', 'args <- commandArgs(trailingOnly = TRUE); invisible(suppressWarnings(compiler::cmpfile(args[2], args[1])))',
                '--args',
            ]
            out_flag_and_exe = [target_rc]
            exec_cmd = False
        elif op == 'build':
            # Compile to bytecode (.Rc), then execute the bytecode with compiler::loadcmp()
            cexe_flags = [
                '--vanilla', '-q', '-s',
                '-e', 'args <- commandArgs(trailingOnly = TRUE); invisible(suppressWarnings(compiler::cmpfile(args[2], args[1])))',
                '--args',
            ]
            out_flag_and_exe = [target_rc]
            exec_cmd = [
                cexe, '--vanilla', '-q', '-s',
                '-e', 'invisible(suppressWarnings(compiler::loadcmp(commandArgs(trailingOnly = TRUE)[1])))',
                '--args',
            ]
        else:
            continue

        version = get_compiler_version(cexe)

        benchmark_compiler_op(code_paths,
                              out_flag_and_exe=out_flag_and_exe,
                              cexe=cexe,
                              exec_cmd=exec_cmd,
                              cexe_flags=cexe_flags,
                              args=args,
                              op=op,
                              compiler_version=version,
                              lang=lang,
                              templated=templated,
                              results=results)


register_language(LangSupport(
    name=Lang('R'),
    exes=[Exec('R')],
    extension=FileExt('R'),
    int_type=TypeName('numeric'),
    runners=[bm_R],
    ops=('check', 'compile', 'build'),
    aliases=('r', 'rlang'),
    tier=3,
    out_binary=DEFAULT_PROGRAM_NAME + '.Rc',
    native_output=_never_native,
    versions=[VersionSpec(('R',), ['--version'], _r_parse_version)],
    limit_args=_r_limits,
    func_emitter=make_func_emitter(
        define=lambda fname, typ, expr, t: f"{fname} <- function(x) {{\n    {expr}\n}}\n",
    ),
    main_header=lambda types, t: 'main <- function() {\n',
    var_decl=lambda typ, t: f"    {typ}_sum <- 0\n",
    call=lambda i, typ, t: f"    {typ}_sum <- {typ}_sum + {function_name(typ, i)}({i})",
    call_terminator='',
    postfix=lambda types: f"    quit(save = 'no', status = as.integer({types[0]}_sum %% 256))\n}}\n\nmain()\n",
))
