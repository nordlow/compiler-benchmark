"""Language support for fortran.

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

FORTRAN_MAX_TOTAL_FUNCS = 10_000
FORTRAN_CAPPED_DIM = 100


def _fortran_limits(args: argparse.Namespace) -> list[str]:
    if args.function_count * args.function_depth > FORTRAN_MAX_TOTAL_FUNCS:
        msg = (f"Warning: Capping Fortran function count/depth from {args.function_count}x{args.function_depth} "
               f"to {FORTRAN_CAPPED_DIM}x{FORTRAN_CAPPED_DIM} due to gfortran module symbol table limits")
        args.function_count = FORTRAN_CAPPED_DIM
        args.function_depth = FORTRAN_CAPPED_DIM
        return [msg]
    return []


def bm_Fortran_using_gcc(results: Results, code_paths: list, args: argparse.Namespace, op: str, templated: bool):
    lang = 'Fortran'
    op_flags = {'check': ['-fsyntax-only'], 'compile': ['-c'], 'build': ['-O0']}.get(op)
    if op_flags is None:
        return None
    out_flag = ['-o', out_binary(lang)] if op == 'build' else []
    for cexe in find_compiler_versions(args, lang, 'gfortran'):
        benchmark_compiler_op(code_paths, out_flag, cexe, True, op_flags,
                              args, op, get_compiler_version(cexe), lang, templated, results)


register_language(LangSupport(
    name=Lang('Fortran'), exes=[Exec('gfortran')], extension=FileExt('f90'), int_type=TypeName('int64'),
    runners=[bm_Fortran_using_gcc],
    ops=('check', 'compile', 'build'),
    aliases=('gfortran',),
    limit_args=_fortran_limits,
    func_emitter=make_func_emitter(
        define=lambda fname, typ, expr, t: (
            f"function {fname}(x) result(r); integer({typ}), value :: x; "
            f"integer({typ}) :: r; r = {expr}; end function\n")),
    prefix=lambda program_name, t: ('module calc\n'
                                    '    use, intrinsic :: iso_fortran_env, only: int64\n'
                                    '    implicit none\n'
                                    'contains\n'),
    main_header=lambda types, t: ('end module calc\n\n'
                                  'program main\n'
                                  '    use, intrinsic :: iso_fortran_env, only: int64\n'
                                  '    use calc\n'
                                  '    implicit none\n'),
    var_decl=lambda typ, t: f"    integer({typ}) :: {typ}_sum\n",
    main_middle=lambda types: ''.join(f"    {typ}_sum = 0\n" for typ in types),
    call=lambda i, typ, t: f"    {typ}_sum = {typ}_sum + {function_name(typ, i)}({i}_{typ})",
    call_terminator='',
    postfix=lambda types: f"    call exit(int(mod({types[0]}_sum, 256_{types[0]})))\nend program main\n",
))
