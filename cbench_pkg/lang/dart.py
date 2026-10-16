"""Language support for dart.

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

def bm_Dart(results: Results, code_paths: list, args: argparse.Namespace, op: str, templated: bool):
    lang = 'Dart'
    cexe = resolve_compiler_path(args, lang, 'dart')
    if not cexe:
        return None

    if op == 'check':
        cexe_flags = ['analyze', '--no-fatal-warnings']
        out_flag_and_exe = []
        exec_cmd = False
    elif op == 'compile':
        cexe_flags = ['compile', 'aot-snapshot']
        out_flag_and_exe = ['-o', out_binary(lang) + '.aot']
        exec_cmd = False
    elif op == 'build':
        cexe_flags = ['compile', 'exe']
        out_flag_and_exe = ['-o', out_binary(lang)]
        exec_cmd = True
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
    name=Lang('Dart'), exes=[Exec('dart')], extension=FileExt('dart'), int_type=TypeName('int'),
    runners=[bm_Dart],
    ops=('check', 'compile', 'build'),
    templated_variants=(False, True),
    tier=3,
    func_emitter=make_func_emitter(
        define=lambda fname, typ, expr, t: (
            f"{typ} {fname}<T extends {typ}>(T x) {{ return {expr}; }}\n" if t
            else f"{typ} {fname}({typ} x) {{ return {expr}; }}\n")),
    prefix=lambda program_name, t: "import 'dart:io';\n\n",
    main_header=lambda types, t: 'void main() {\n',
    var_decl=lambda typ, t: f"    {typ} {typ}_sum = 0;\n",
    call=lambda i, typ, t: (f"    {typ}_sum += {function_name(typ, i)}<{typ}>({i})" if t else plain_call(i, typ, t)),
    postfix=lambda types: f"    exit({types[0]}_sum % 256);\n}}\n",
))
