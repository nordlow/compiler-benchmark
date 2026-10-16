"""Language support for hylo.

Self-contained block: runner(s) + register_language call. To add a new language,
drop a new module here and it is picked up automatically by the engine.
"""
import argparse
import copy
import os
import subprocess as sp
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

def bm_Hylo(results: Results, code_paths, args: argparse.Namespace, op, templated: bool):
    lang = 'Hylo'
    cexe = resolve_compiler_path(args, lang, 'hc')
    if not cexe:
        return
    if op == 'build':
        cexe_flags = []
        out_flag_and_exe = ['-o', out_binary(lang)]
    elif op == 'check':
        cexe_flags = ['--typecheck']
        out_flag_and_exe = []
    else:
        return None
    version_run = sp.run([cexe, '--version'], stdout=sp.PIPE, stderr=sp.PIPE)
    version = version_run.stdout.decode('utf-8').split()[-1]
    benchmark_compiler_op(code_paths,
                          out_flag_and_exe=out_flag_and_exe,
                          cexe=cexe,
                          exec_cmd=True,
                          cexe_flags=cexe_flags,
                          args=args,
                          op=op,
                          compiler_version=version,
                          lang=lang,
                          templated=templated,
                          results=results)


register_language(LangSupport(
    name=Lang('Hylo'), exes=[Exec('hc')], extension=FileExt('hylo'), int_type=TypeName('Int64'),
    runners=[bm_Hylo],
    ops=('check', 'build'),
    templated_variants=(False, True),
    func_emitter=make_func_emitter(
        define=lambda fname, typ, expr, t: (
            f"func {fname}<T: BinaryInteger>(x: T) -> T {{ return {expr} }}\n" if t
            else f"func {fname}(x: {typ}) -> {typ} {{ return {expr} }}\n"),
        chain=lambda typ, t, prev, c: f"x + {prev}(x: x) + {c}",
    ),
    prefix=lambda program_name, t: 'import Foundation\n\n',
    main_header=lambda types, t: 'func main() {\n',
    var_decl=lambda typ, t: f"    var {typ}_sum: {typ} = 0;\n",
    call=lambda i, typ, t: f"    {typ}_sum += {function_name(typ, i)}(x: {i})",
    postfix=lambda types: f"    exit(Int32({types[0]}_sum))\n}}\n",
))
