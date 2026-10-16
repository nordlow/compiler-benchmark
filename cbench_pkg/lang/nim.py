"""Language support for nim.

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

NIM_MAX_DEPTH = 50  # compiler hard limit on recursive generic instantiations


def bm_Nim(results: Results, code_paths, args: argparse.Namespace, op, templated: bool, cexe_flags=None):
    lang = 'Nim'
    cexe = resolve_compiler_path(args, lang, 'nim')
    if not cexe:
        return None

    common_flags = ['--hints:off', '--checks:off', '--stacktrace:off', '--errorMax:1']

    if op == 'check':
        cexe_flags = common_flags + ['check']
        out_flag_and_exe = []
    elif op == 'build':
        cexe_flags = common_flags + ['c', '--mm:refc', '--opt:none']
        out_flag_and_exe = ['--out:' + out_binary(lang)]
    else:
        return None

    version = get_compiler_version(cexe)
    benchmark_compiler_op(code_paths,
                          out_flag_and_exe=out_flag_and_exe,
                          cexe=cexe,
                          exec_cmd=(op == 'build'),
                          cexe_flags=cexe_flags,
                          args=args,
                          op=op,
                          compiler_version=version,
                          lang=lang,
                          templated=templated,
                          results=results)


def _nim_limits(args: argparse.Namespace) -> list[str]:
    if args.function_depth > NIM_MAX_DEPTH:
        msg = (f"Warning: Capping Nim function depth (--function-depth) from {args.function_depth} "
               f"to {NIM_MAX_DEPTH} due to compiler generic recursion limit")
        args.function_depth = NIM_MAX_DEPTH
        return [msg]
    return []


register_language(LangSupport(
    name=Lang('Nim'), exes=[Exec('nim')], extension=FileExt('nim'), int_type=TypeName('int64'),
    runners=[bm_Nim],
    ops=('check', 'build'),
    templated_variants=(False, True),
    limit_args=_nim_limits,
    func_emitter=make_func_emitter(
        define=lambda fname, typ, expr, t: (
            f"proc {fname}[T](x: T): T =\n  return {expr}\n" if t
            else f"proc {fname}(x: {typ}): {typ} = \n  return {expr}\n")),
    main_header=lambda types, t: 'when isMainModule:\n',
    var_decl=lambda typ, t: f"    var {typ}_sum: {typ} = 0;\n",
    call=lambda i, typ, t: (f"    {typ}_sum += {function_name(typ, i)}[{typ}]({i})" if t else plain_call(i, typ, t)),
    call_terminator='',
    postfix=lambda types: f"    quit(int({types[0]}_sum))\n\n",
))
