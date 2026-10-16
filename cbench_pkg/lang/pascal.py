"""Language support for pascal.

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

def bm_Pascal(results: Results, code_paths, args: argparse.Namespace, op, templated: bool):
    lang = 'Pascal'
    cexe = resolve_compiler_path(args, lang, 'fpc')
    if not cexe:
        return None

    if op in ('check', 'compile'):
        cexe_flags = ['-Cn', '-O-']
        out_flag_and_exe = []
    elif op == 'build':
        cexe_flags = ['-O-', '-B', '-Aas']
        out_flag_and_exe = ['-o' + out_binary(lang)]
    else:
        return None

    try:
        version = get_compiler_version(cexe)
    except Exception:
        version = 'unknown'

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
    name=Lang('Pascal'), exes=[Exec('fpc')], extension=FileExt('pas'), int_type=TypeName('Int64'),
    runners=[bm_Pascal],
    ops=('check', 'compile', 'build'),
    aliases=('fpc',),
    versions=[VersionSpec(('fpc',), ['-iV'])],
    func_emitter=make_func_emitter(
        define=lambda fname, typ, expr, t: f"function {fname}(x: {typ}): {typ}; begin {fname} := {expr}; end;\n"),
    prefix=lambda program_name, t: f"program {program_name};\n\n",
    main_header=lambda types, t: 'var\n',
    var_decl=lambda typ, t: f"  {typ}_sum: {typ};\n",
    main_middle=lambda types: 'begin\n' + ''.join(f"  {typ}_sum := 0;\n" for typ in types),
    call=lambda i, typ, t: f"  {typ}_sum := {typ}_sum + {function_name(typ, i)}({i})",
    postfix=lambda types: f"  Halt({types[0]}_sum mod 256);\nend.\n",
))
