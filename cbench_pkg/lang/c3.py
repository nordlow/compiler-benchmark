"""Language support for c3.

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

def bm_C3(results: Results, code_paths, args: argparse.Namespace, op, templated: bool):
    lang = 'C3'
    cexe = resolve_compiler_path(args, lang, 'c3c')
    if not cexe:
        return

    common_flags = ['-q', '-O0']

    if op == 'check':
        cexe_flags = ['compile-only'] + common_flags + ['-C']
        out_flag_and_exe = []
        exec_cmd = False
    elif op == 'compile':
        cexe_flags = ['compile-only'] + common_flags
        out_flag_and_exe = []
        exec_cmd = False
    elif op == 'build':
        cexe_flags = ['compile'] + common_flags
        out_flag_and_exe = ['-o', out_binary(lang)]
        exec_cmd = True
    else:
        return

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


def _c3_parse_version(out: str, default: str) -> str | None:
    return out.split(':')[1].split()[0] if ':' in out else None


register_language(LangSupport(
    name=Lang('C3'), exes=[Exec('c3c')], extension=FileExt('c3'), int_type=TypeName('long'),
    runners=[bm_C3],
    ops=('check', 'compile', 'build'),
    templated_variants=(False, True),
    versions=[VersionSpec(('c3c',), ['--version'], _c3_parse_version)],
    func_emitter=make_func_emitter(
        define=lambda fname, typ, expr, t: (
            f"fn Type {fname}(Type x) <Type> {{ return {expr}; }}\n" if t
            else f"fn {typ} {fname}({typ} x) {{ return {expr}; }}\n"),
        leaf=lambda typ, t, c: (f"x + (Type){c}" if t else f"x + {c}"),
    ),
    prefix=lambda program_name, t: 'module calc<T>;\n\n' if t else 'module calc;\n\n',
    main_header=lambda types, t: 'module main;\n\nimport calc;\n\nfn int main(String[] args) {\n',
    var_decl=lambda typ, t: f"    {typ} {typ}_sum = 0;\n",
    call=lambda i, typ, t: (
        f"    {typ}_sum += calc::{function_name(typ, i)}{{{typ}}}({i})" if t
        else f"    {typ}_sum += calc::{function_name(typ, i)}({i})"),
    postfix=lambda types: f"        return (int)({types[0]}_sum);\n}}\n",
))
