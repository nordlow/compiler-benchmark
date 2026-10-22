"""Language support for goose.

Self-contained block: runner(s) + register_language call. To add a new language,
drop a new module here and it is picked up automatically by the engine.
"""
import argparse
import os

from ..compiler import benchmark_compiler_op, out_binary
from ..types import (
    Exec,
    FileExt,
    Lang,
    LangSupport,
    Results,
    TypeName,
    VersionSpec,
    make_func_emitter,
    plain_call,
    register_language,
)
from ..version import get_compiler_version, resolve_compiler_path


def bm_Goose(results: Results, code_paths, args: argparse.Namespace, op, templated: bool):
    lang = 'Goose'
    cexe = resolve_compiler_path(args, lang, 'goose')
    if not cexe:
        local_goose = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../.omp/tmp/goose/build/goose'))
        if os.path.exists(local_goose):
            cexe = local_goose
        else:
            return

    if op == 'check':
        cexe_flags = ['check']
        out_flag_and_exe = []
        exec_cmd = False
    elif op == 'build':
        cexe_flags = ['build']
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


def _goose_build_cmd(cexe, cexe_flags, out_flags, src_name):
    return [cexe] + cexe_flags + [src_name] + out_flags


def _goose_parse_version(out: str, default: str) -> str | None:
    parts = out.strip().split()
    return parts[-1] if parts else default


register_language(LangSupport(
    name=Lang('Goose'), exes=[Exec('goose')], extension=FileExt('goose'), int_type=TypeName('i64'),
    runners=[bm_Goose],
    ops=('check', 'build'),
    templated_variants=(False, True),
    versions=[VersionSpec(('goose',), ['version'], _goose_parse_version)],
    build_cmd=_goose_build_cmd,
    func_emitter=make_func_emitter(
        define=lambda fname, typ, expr, t: (
            f"fn {fname}<T>(x: T) -> T {{ return {expr}; }}\n" if t
            else f"fn {fname}(x: {typ}) -> {typ} {{ return {expr}; }}\n"),
    ),
    prefix=lambda program_name, t: f"// program {program_name}\n\n",
    main_header=lambda types, t: 'fn main() {\n',
    var_decl=lambda typ, t: f"    var {typ}_sum: {typ} = 0;\n",
    call=lambda i, typ, t: plain_call(i, typ, t),
    postfix=lambda types: f"    exit({types[0]}_sum);\n}}\n",
))
