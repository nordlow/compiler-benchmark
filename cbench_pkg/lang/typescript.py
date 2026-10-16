"""Language support for typescript.

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
from ._shared import typescript_limits

def bm_TypeScript(results: Results, code_paths: list, args: argparse.Namespace, op: str, templated: bool):
    lang = 'TypeScript'
    cexe = resolve_compiler_path(args, lang, 'tsc')
    if not cexe:
        return None

    target_js = out_binary(lang)
    node_exe = which('node')

    if op == 'check':
        cexe_flags = ['--noEmit']
        out_flag_and_exe = []
        exec_cmd = False
    elif op == 'compile':
        cexe_flags = ['--ignoreDeprecations', '6.0', '--outFile', target_js]
        out_flag_and_exe = []
        exec_cmd = False
    elif op == 'build':
        cexe_flags = ['--ignoreDeprecations', '6.0', '--outFile', target_js]
        out_flag_and_exe = []
        exec_cmd = [node_exe] if node_exe else False
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
    name=Lang('TypeScript'), exes=[Exec('tsc')], extension=FileExt('ts'), int_type=TypeName('number'),
    runners=[bm_TypeScript],
    ops=('check', 'compile', 'build'),
    templated_variants=(False, True),
    aliases=('ts', 'tsc'),
    tier=3,
    limit_args=typescript_limits,
    out_binary=DEFAULT_PROGRAM_NAME + '.js',
    native_output=_never_native,
    func_emitter=make_func_emitter(
        define=lambda fname, typ, expr, t: (
            f"function {fname}<T extends {typ}>(x: T): {typ} {{ return {expr}; }}\n" if t
            else f"function {fname}(x: {typ}): {typ} {{ return {expr}; }}\n")),
    prefix=lambda program_name, t: 'declare var process: any;\n\n',
    main_header=lambda types, t: 'function main() {\n',
    var_decl=lambda typ, t: f"    var {typ}_sum: {typ} = 0;\n",
    call=lambda i, typ, t: (f"    {typ}_sum += {function_name(typ, i)}<{typ}>({i})" if t else plain_call(i, typ, t)),
    postfix=lambda types: f"    process.exit({types[0]}_sum % 256);\n}}\n\nmain();\n",
))
