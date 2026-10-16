"""Language support for v.

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

def bm_V(results: Results, code_paths, args: argparse.Namespace, op, templated: bool):
    lang = 'V'
    cexe = resolve_compiler_path(args, lang, 'v')
    if not cexe:
        return
    if op == 'check':
        cexe_flags = ['-check']
        out_flag_and_exe = []
        exec_cmd = False
    elif op == 'build':
        cexe_flags = []
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
    name=Lang('V'), exes=[Exec('v')], extension=FileExt('v'), int_type=TypeName('i64'),
    runners=[bm_V],
    ops=('check', 'build'),
    templated_variants=(False, True),
    func_emitter=make_func_emitter(
        define=lambda fname, typ, expr, t: (
            f"fn {fname}[T](x T) T {{ return {expr} }}\n" if t
            else f"fn {fname}(x {typ}) {typ} {{ return {expr} }}\n"),
        chain=lambda typ, t, prev, c: (f"x + {prev}[{typ}](x) + {c}" if t else f"x + {prev}(x) + {c}"),
    ),
    main_header=lambda types, t: 'fn main() {\n',
    var_decl=lambda typ, t: f"    mut {typ}_sum := {typ}(0)\n",
    call=lambda i, typ, t: (f"    {typ}_sum += {function_name(typ, i)}[{typ}]({i})" if t else plain_call(i, typ, t)),
    call_terminator='',
    postfix=lambda types: f"    exit(int({types[0]}_sum >> 32))\n}}\n",
))
