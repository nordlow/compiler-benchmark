"""Language support for Bend.

Self-contained block: runner(s) + register_language call. To add a new language,
drop a new module here and it is picked up automatically by the engine.
"""
import argparse

from ..compiler import benchmark_compiler_op, out_binary
from ..types import (
    DEFAULT_PROGRAM_NAME,
    Exec,
    FileExt,
    Lang,
    LangSupport,
    Results,
    TypeName,
    VersionSpec,
    function_name,
    make_func_emitter,
    register_language,
)
from ..version import get_compiler_version, resolve_compiler_path


def _bend_build_cmd(cexe, cexe_flags, out_flags, src_name):
    return [cexe, src_name] + cexe_flags + out_flags


def bm_Bend(results: Results, code_paths, args: argparse.Namespace, op: str, templated: bool):
    lang = 'Bend'
    cexe = resolve_compiler_path(args, lang, 'bend')
    if not cexe:
        return

    if op == 'check':
        cexe_flags = ['--check-only']
        out_flag_and_exe = []
        exec_cmd = False
    elif op == 'build':
        cexe_flags = []
        out_flag_and_exe = ['-o', out_binary(lang)]
        exec_cmd = True
    else:
        return

    try:
        version = get_compiler_version(cexe)
    except (Exception, OSError):
        version = 'unknown'

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
    name=Lang('Bend'),
    exes=[Exec('bend')],
    extension=FileExt('bend'),
    int_type=TypeName('U32'),
    runners=[bm_Bend],
    ops=('check', 'build'),
    templated_variants=(False, True),
    aliases=('bendlang',),
    tier=3,
    out_binary=DEFAULT_PROGRAM_NAME,
    versions=[VersionSpec(('bend',), ['version'])],
    build_cmd=_bend_build_cmd,
    func_emitter=make_func_emitter(
        define=lambda fname, typ, expr, _t: f"def {fname}(+x: {typ}) -> {typ}:\n    {expr}\n\n",
        leaf=lambda typ, _t, c: f"(x + {c} : {typ})",
        chain=lambda typ, _t, prev, c: f"(x + {prev}(x) + {c} : {typ})",
    ),
    prefix=lambda _program_name, _t: 'import Base\n\n',
    main_header=lambda _types, _t: 'def main() -> U32:\n',
    var_decl=lambda typ, _t: f"    {typ}_sum = {{{0} : {typ}}}\n",
    call=lambda i, typ, _t: f"    {typ}_sum = ({typ}_sum + {function_name(typ, i)}({i}) : {typ})",
    call_terminator='',
    postfix=lambda types: f"    {types[0]}_sum\n",
))
