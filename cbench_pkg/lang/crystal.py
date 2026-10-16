"""Language support for crystal.

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
from ._shared import crystal_limits

def bm_Crystal(results: Results, code_paths, args: argparse.Namespace, op, templated: bool):
    lang = 'Crystal'
    cexe = resolve_compiler_path(args, lang, 'crystal')
    if not cexe:
        return None

    if op == 'check':
        cexe_flags = ['build', '--no-codegen']
        out_flag_and_exe = []
    elif op == 'build':
        cexe_flags = ['build', '--no-debug']
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


register_language(LangSupport(
    name=Lang('Crystal'), exes=[Exec('crystal')], extension=FileExt('cr'), int_type=TypeName('Int64'),
    runners=[bm_Crystal],
    ops=('check', 'build'),
    templated_variants=(False, True),
    tier=3,
    limit_args=crystal_limits,
    func_emitter=make_func_emitter(
        define=lambda fname, typ, expr, t: (
            f"def {fname}(x); return {expr}; end\n" if t
            else f"def {fname}(x : {typ}) : {typ}; return {expr}; end\n")),
    main_header=lambda types, t: 'def main\n',
    var_decl=lambda typ, t: f"    {typ.lower()}_sum = 0_i64\n",
    call=lambda i, typ, t: f"    {typ.lower()}_sum += {function_name(typ, i)}({i}_i64)",
    call_terminator='',
    postfix=lambda types: f"    exit(({types[0].lower()}_sum % 256).to_i32)\nend\n\nmain()\n",
))
