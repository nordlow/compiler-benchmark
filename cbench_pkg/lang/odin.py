"""Language support for odin.

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

def bm_Odin(results: Results, code_paths, args: argparse.Namespace, op, templated: bool):
    lang = 'Odin'
    cexe = resolve_compiler_path(args, lang, 'odin')
    if not cexe:
        return None

    if op == 'build':
        cexe_flags = ['build', '-build-mode:exe', '-linker:lld']
        out_flag_and_exe = ['-out:' + out_binary(lang)]
    elif op == 'check':
        cexe_flags = ['check']
        out_flag_and_exe = []
    else:
        return None

    version = get_compiler_version(cexe)
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


def _odin_parse_version(out: str, default: str) -> str | None:
    parts = out.split()
    return parts[2] if len(parts) >= 3 else default


def _odin_build_cmd(cexe, cexe_flags, out_flags, src_name):
    # `odin <verb> <src> -file <other flags> <out flags>`
    verb = [cexe_flags[0]] if cexe_flags else []
    remaining = cexe_flags[1:] if cexe_flags else []
    return [cexe] + verb + [src_name, '-file'] + remaining + out_flags


register_language(LangSupport(
    name=Lang('Odin'), exes=[Exec('odin')], extension=FileExt('odin'), int_type=TypeName('i64'),
    runners=[bm_Odin],
    ops=('check', 'build'),
    templated_variants=(False, True),
    versions=[VersionSpec(('odin',), ['version'], _odin_parse_version)],
    build_cmd=_odin_build_cmd,
    func_emitter=make_func_emitter(
        define=lambda fname, typ, expr, t: (
            f"{fname} :: proc(x: $T) -> T {{ return {expr} }}\n" if t
            else f"{fname} :: proc(x: {typ}) -> {typ} {{ return {expr} }}\n"),
    ),
    prefix=lambda program_name, t: f"package {program_name}\n\nimport \"core:os\"\n\n",
    main_header=lambda types, t: 'main :: proc() {\n',
    var_decl=lambda typ, t: f"    {typ}_sum: {typ} = 0\n",
    call=lambda i, typ, t: (f"    {typ}_sum += {function_name(typ, i)}({typ}({i}))" if t else plain_call(i, typ, t)),
    call_terminator='',
    postfix=lambda types: f"    os.exit(int({types[0]}_sum))\n}}\n",
))
