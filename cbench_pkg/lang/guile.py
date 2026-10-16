"""Language support for guile.

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

GUILE_MAX_TOTAL_FUNCS = 5_000
GUILE_CAPPED_DIM = 70


def _guile_limits(args: argparse.Namespace) -> list[str]:
    if args.function_count * args.function_depth > GUILE_MAX_TOTAL_FUNCS:
        msg = (f"Warning: Capping Guile function count/depth from {args.function_count}x{args.function_depth} "
               f"to {GUILE_CAPPED_DIM}x{GUILE_CAPPED_DIM} due to Tree-IL CPS compiler scaling limits")
        args.function_count = GUILE_CAPPED_DIM
        args.function_depth = GUILE_CAPPED_DIM
        return [msg]
    return []


def bm_Guile(results: Results, code_paths: list, args: argparse.Namespace, op: str, templated: bool):
    lang = 'Guile'
    cexe = resolve_compiler_path(args, lang, 'guild') or resolve_compiler_path(args, lang, 'guile')
    if not cexe:
        return None

    guile_exe = resolve_compiler_path(args, lang, 'guile') or which('guile')
    target_go = out_binary(lang)
    version = get_compiler_version(cexe)
    if op == 'check':
        with tempfile.NamedTemporaryFile(suffix='.check_tmp') as tmp_file:
            benchmark_compiler_op(code_paths,
                                  out_flag_and_exe=[],
                                  cexe=cexe,
                                  exec_cmd=False,
                                  cexe_flags=['compile', '-W0', '-o', tmp_file.name],
                                  args=args,
                                  op=op,
                                  compiler_version=version,
                                  lang=lang,
                                  templated=templated,
                                  results=results)
    elif op == 'compile':
        benchmark_compiler_op(code_paths,
                              out_flag_and_exe=[],
                              cexe=cexe,
                              exec_cmd=False,
                              cexe_flags=['compile', '-W0', '-o', target_go],
                              args=args,
                              op=op,
                              compiler_version=version,
                              lang=lang,
                              templated=templated,
                              results=results)
    elif op == 'build':
        benchmark_compiler_op(code_paths,
                              out_flag_and_exe=[],
                              cexe=cexe,
                              exec_cmd=[guile_exe, '-c', '(load-compiled (car (reverse (command-line))))'] if guile_exe else False,
                              cexe_flags=['compile', '-W0', '-o', target_go],
                              args=args,
                              op=op,
                              compiler_version=version,
                              lang=lang,
                              templated=templated,
                              results=results)
    else:
        return None


register_language(LangSupport(
    name=Lang('Guile'), exes=[Exec('guild')], extension=FileExt('scm'), int_type=TypeName('int'),
    runners=[bm_Guile],
    ops=('check', 'compile', 'build'),
    aliases=('guild',),
    tier=3,
    limit_args=_guile_limits,
    out_binary=DEFAULT_PROGRAM_NAME + '.go',
    native_output=_never_native,
    func_emitter=make_func_emitter(
        define=lambda fname, typ, expr, t: f"(define ({fname} x) {expr})\n",
        leaf=lambda typ, t, c: f"(+ x {c})",
        chain=lambda typ, t, prev, c: f"(+ x ({prev} x) {c})",
    ),
    main_header=lambda types, t: '(define (main)\n',
    main_middle=lisp_let_middle,
    call=lambda i, typ, t: f"    (set! {typ}_sum (+ {typ}_sum ({function_name(typ, i)} {i})))",
    call_terminator='',
    postfix=lambda types: f"    {types[0]}_sum))\n(exit (main))\n",
))
