"""Language support for ocaml.

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
from ._shared import _ocaml_julia_limits

def bm_OCaml(results: Results, code_paths, args: argparse.Namespace, op, templated: bool, bytecode):
    lang = 'OCaml'
    cexe = resolve_compiler_path(args, lang, 'ocamlc' if bytecode else 'ocamlopt')
    if not cexe:
        return
    if op == 'check':
        cexe_flags = ['-stop-after', 'typing', '-c']
        out_flag_and_exe = []
        exec_cmd = False
    elif op == 'build':
        cexe_flags = ['-c'] if bytecode else ['-linscan']
        out_flag_and_exe = ['-o', out_binary(lang)]
        exec_cmd = ([which('ocamlrun')] if bytecode else True)
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
    name=Lang('OCaml'), exes=[Exec('ocamlc'), Exec('ocamlopt')], extension=FileExt('ml'), int_type=TypeName('float'),
    runners=[
        lambda r, cp, a, op, t: bm_OCaml(r, cp, a, op, t, bytecode=False),
        lambda r, cp, a, op, t: bm_OCaml(r, cp, a, op, t, bytecode=True),
    ],
    ops=('check', 'build'),
    tier=3,
    native_output=lambda cexe: not os.path.basename(cexe).startswith('ocamlc'),  # ocamlc emits bytecode
    limit_args=_ocaml_julia_limits,
    func_emitter=make_func_emitter(
        define=lambda fname, typ, expr, t: f"let {fname} x = {expr}\n",
        leaf=lambda typ, t, c: f"x +. {c}.0",
        chain=lambda typ, t, prev, c: f"x +. ({prev} x) +. {c}.0",
    ),
    main_header=lambda types, t: 'let () = \n',
    var_decl=lambda typ, t: f"    let {typ}_sum = 0.0 in\n",
    call=lambda i, typ, t: f"    let {typ}_sum = {typ}_sum +. ({function_name(typ, i)} {i}.0) in",
    call_terminator='',
    postfix=lambda types: f"    exit (if {types[0]}_sum = 42.0 then 1 else 0)\n",
))
