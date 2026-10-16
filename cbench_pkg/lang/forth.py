"""Language support for Forth (gforth).

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


FORTH_MAX_TOTAL_FUNCS = 10_000
FORTH_CAPPED_DIM = 100


def _forth_limits(args: argparse.Namespace) -> list[str]:
    if args.function_count * args.function_depth > FORTH_MAX_TOTAL_FUNCS:
        msg = (f"Warning: Capping Forth function count/depth from {args.function_count}x{args.function_depth} "
               f"to {FORTH_CAPPED_DIM}x{FORTH_CAPPED_DIM} due to Forth dictionary limits")
        args.function_count = FORTH_CAPPED_DIM
        args.function_depth = FORTH_CAPPED_DIM
        return [msg]
    return []


def _forth_leaf(typ: str, templated: bool, c: str) -> str:
    # Forth: ( x -- x )  x + c  =>  {c} +
    return f"{c} +"


def _forth_chain(typ: str, templated: bool, prev: str, c: str) -> str:
    # Forth: x + prev(x) + c  =>  dup {prev} + {c} +
    return f"dup {prev} + {c} +"


def bm_Forth_using_gforth(results: Results, code_paths, args: argparse.Namespace, op, templated: bool):
    lang = 'Forth'
    cexe = resolve_compiler_path(args, lang, 'gforth')
    if not cexe:
        return
    if op == 'check':
        # gforth interprets the source file; loading it validates syntax and
        # executes the program, so this doubles as the check/interpretation step.
        cexe_flags = []
        out_flag_and_exe = []
        exec_cmd = False
    else:
        return None
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
    name=Lang('Forth'), exes=[Exec('gforth')],
    extension=FileExt('fs'), int_type=TypeName('int'),
    runners=[bm_Forth_using_gforth],
    ops=('check',),
    templated_variants=(False,),
    aliases=('forth',),
    tier=3,
    native_output=_never_native,
    versions=[VersionSpec(('gforth',), ['--version'])],
    limit_args=_forth_limits,
    func_emitter=make_func_emitter(
        define=lambda fname, typ, expr, t: f": {fname} ( x -- x ) {expr} ;\n",
        leaf=_forth_leaf,
        chain=_forth_chain,
    ),
    main_header=lambda types, t: ": main ( -- ) 0 ",
    var_decl=lambda typ, t: "",
    main_middle=lambda types: "",
    call=lambda i, typ, t: f"{i} {function_name(typ, i)} +",
    call_terminator='',
    postfix=lambda types: "cr . ;\nmain bye\n",
))
