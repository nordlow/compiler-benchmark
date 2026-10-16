"""Language support for pareas.

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

def bm_Pareas(results: Results, code_paths, args: argparse.Namespace, op, templated: bool):
    lang = 'Pareas'
    cexe = resolve_compiler_path(args, lang, 'pareas')
    if not cexe:
        return None
    benchmark_compiler_op(code_paths,
                          out_flag_and_exe=['-o', out_binary(lang)],
                          cexe=cexe,
                          exec_cmd=False,
                          cexe_flags=['--check'] if op == 'check' else [],
                          args=args,
                          op=op,
                          compiler_version='unknown',
                          lang=lang,
                          templated=templated,
                          results=results)


register_language(LangSupport(
    name=Lang('Pareas'), exes=[Exec('pareas')], extension=FileExt('par'), int_type=TypeName('int'),
    runners=[bm_Pareas],
    ops=('check', 'build'),
    versions=[VersionSpec(('pareas',), fixed='unknown')],
    func_emitter=make_func_emitter(
        define=lambda fname, typ, expr, t: f"fn {fname}[x: {typ}]: {typ} {{ return {expr}; }}\n",
        chain=lambda typ, t, prev, c: f"x + {prev}[x] + {c}",
    ),
    main_header=lambda types, t: 'fn main[]: int {\n',
    var_decl=lambda typ, t: f"    var {typ}_sum: {typ} = 0;\n",
    call=lambda i, typ, t: f"    {typ}_sum = {typ}_sum + {function_name(typ, i)}[{i}]",
    postfix=lambda types: f"    return {types[0]}_sum;\n}}\n",
))
