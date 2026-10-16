"""Language support for c.

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
from ..compiler import benchmark_compiler_op, build_compiler_cmd, out_directory, out_binary, bm_C_and_Cxx_using_gcc, bm_C_and_Cxx_using_clang, get_gcc_lib_dir

CUIK_MAX_DIM = 100  # compiler stability limit


def bm_C_using_cproc(results: Results, code_paths: list, args: argparse.Namespace, op: str, templated: bool):
    lang = 'C'
    cexe = resolve_compiler_path(args, lang, 'cproc')
    if not cexe:
        return

    if op == 'check':
        cexe_flags = ['-emit-qbe']
        out_flag_and_exe = ['-o', '/dev/null']
    elif op == 'compile':
        cexe_flags = ['-c']
        out_flag_and_exe = ['-o', '/dev/null']
    elif op == 'build':
        cexe_flags = []
        gcc_lib_dir = get_gcc_lib_dir()
        if gcc_lib_dir:
            cexe_flags.append(f'-L{gcc_lib_dir}')
        out_flag_and_exe = ['-o', out_binary(lang)]
    else:
        return None

    benchmark_compiler_op(code_paths,
                          out_flag_and_exe=out_flag_and_exe,
                          cexe=cexe,
                          exec_cmd=(op == 'build'),
                          cexe_flags=cexe_flags,
                          args=args,
                          op=op,
                          compiler_version='unknown',
                          lang=lang,
                          templated=templated,
                          results=results)


def bm_C_using_tcc(results: Results, code_paths: list, args: argparse.Namespace, op: str, templated: bool):
    lang = 'C'
    cexe = resolve_compiler_path(args, lang, 'tcc')
    if not cexe:
        return

    if op == 'check':
        cexe_flags = ['-c']
        out_flag_and_exe = ['-o', '/dev/null']
    elif op == 'compile':
        cexe_flags = ['-c']
        out_flag_and_exe = []
    elif op == 'build':
        cexe_flags = []
        out_flag_and_exe = ['-o', out_binary(lang)]
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


def bm_C_using_cuik(results: Results, code_paths: list, args: argparse.Namespace, op: str, templated: bool):
    lang = 'C'
    cexe = resolve_compiler_path(args, lang, 'cuik')
    if not cexe:
        return

    # Cuik-only stability limit: other C compilers keep the full size.
    if args.function_count > CUIK_MAX_DIM or args.function_depth > CUIK_MAX_DIM:
        args = copy.deepcopy(args)
        if args.function_count > CUIK_MAX_DIM:
            print(f"Warning: Capping Cuik function count (--function-count) from {args.function_count} "
                  f"to {CUIK_MAX_DIM} due to compiler stability limit")
            args.function_count = CUIK_MAX_DIM
        if args.function_depth > CUIK_MAX_DIM:
            print(f"Warning: Capping Cuik function depth (--function-depth) from {args.function_depth} "
                  f"to {CUIK_MAX_DIM} due to compiler stability limit")
            args.function_depth = CUIK_MAX_DIM

    if op == 'check':
        cexe_flags = ['-c', '-xe']
        out_flag_and_exe = []
    elif op == 'compile':
        cexe_flags = ['-c']
        out_flag_and_exe = []
    elif op == 'build':
        cexe_flags = []
        out_flag_and_exe = ['-o', out_binary(lang)]
    else:
        return None

    benchmark_compiler_op(code_paths,
                          out_flag_and_exe=out_flag_and_exe,
                          cexe=cexe,
                          exec_cmd=(op == 'build'),
                          cexe_flags=cexe_flags,
                          args=args,
                          op=op,
                          compiler_version="~master",
                          lang=lang,
                          templated=templated,
                          results=results)


register_language(LangSupport(
    name=Lang('C'), exes=[Exec('tcc'), Exec('cuik'), Exec('cproc'), Exec('gcc'), Exec('clang')],
    extension=FileExt('c'), int_type=TypeName('long'),
    runners=[
        bm_C_using_tcc,
        bm_C_using_cuik,
        bm_C_using_cproc,
        lambda r, cp, a, op, t: bm_C_and_Cxx_using_gcc(r, 'C', cp, a, op, t),
        lambda r, cp, a, op, t: bm_C_and_Cxx_using_clang(r, 'C', cp, a, op, t),
    ],
    ops=('check', 'compile', 'build'),
    exe_tiers={'tcc': 1, 'cuik': 1, 'cproc': 1},
    versions=[
        VersionSpec(('cproc',), fixed='unknown'),
        VersionSpec(('cuik',), fixed='~master'),
        VersionSpec(('tcc',), ['-v']),
    ],
    func_emitter=make_func_emitter(
        define=lambda fname, typ, expr, t: f"{typ} {fname}({typ} x) {{ return {expr}; }}\n"),
    main_header=lambda types, t: 'int main(void) {\n',
    var_decl=lambda typ, t: f"    {typ} {typ}_sum = 0;\n",
    postfix=lambda types: f"    return {types[0]}_sum;\n}}\n",
))
