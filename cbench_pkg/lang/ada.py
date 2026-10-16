"""Language support for ada.

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

ADA_MAX_TOTAL_FUNCS = 10_000
ADA_CAPPED_DIM = 100


def _ada_limits(args: argparse.Namespace) -> list[str]:
    if args.function_count * args.function_depth > ADA_MAX_TOTAL_FUNCS:
        msg = (f"Warning: Capping Ada function count/depth from {args.function_count}x{args.function_depth} "
               f"to {ADA_CAPPED_DIM}x{ADA_CAPPED_DIM} due to gnatbind & elaborator scaling limits")
        args.function_count = ADA_CAPPED_DIM
        args.function_depth = ADA_CAPPED_DIM
        return [msg]
    return []


def bm_Ada_using_gcc(results: Results, code_paths: list, args: argparse.Namespace, op: str, templated: bool):
    lang = 'Ada'
    if op == 'check':
        cexe_flags = ['compile', '-q', '-u', '-gnatc']
        out_flag_and_exe = []
        exec_cmd = False
    elif op == 'compile':
        cexe_flags = ['compile', '-q', '-u', '-c']
        out_flag_and_exe = []
        exec_cmd = False
    elif op == 'build':
        cexe_flags = ['make', '-q']
        out_flag_and_exe = ['-o', out_binary(lang)]
        exec_cmd = True
    else:
        return None
    for cexe in find_compiler_versions(args, lang, 'gnat'):
        benchmark_compiler_op(code_paths, out_flag_and_exe, cexe, exec_cmd, cexe_flags, args, op,
                              get_compiler_version(cexe), lang, templated, results)


register_language(LangSupport(
    name=Lang('Ada'), exes=[Exec('gnat')], extension=FileExt('adb'), int_type=TypeName('Long_Integer'),
    runners=[bm_Ada_using_gcc],
    ops=('check', 'build'),
    limit_args=_ada_limits,
    func_emitter=make_func_emitter(
        define=lambda fname, typ, expr, t: f"   function {fname} (x: {typ}) return {typ} is ({expr});\n"),
    prefix=lambda program_name, t: 'with System;\n\nwith GNAT.OS_Lib;\n\n',
    main_header=lambda types, t: 'procedure Main is\n',
    var_decl=lambda typ, t: f"   {typ}_sum : {typ} := 0;\n",
    main_middle=lambda types: 'begin\n',
    call=lambda i, typ, t: f"   {typ}_sum := {typ}_sum + {function_name(typ, i)}({i})",
    postfix=lambda types: f"   GNAT.OS_Lib.OS_Exit(Integer({types[0]}_sum));\nend Main;\n",
    # Ada: the procedure header must precede the (nested) function definitions,
    # and gnat expects the file name to match the unit (no per-run suffix).
    order_sections=lambda write_header, write_defs: (write_header(), write_defs()),
    source_filename=lambda program_name, t, run_ix, ext: f"{program_name}{'_t' if t else ''}.{ext}",
))
