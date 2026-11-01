"""Language support for MoonBit.

Self-contained block: runner(s) + register_language call. To add a new language,
drop a new module here and it is picked up automatically by the engine.
"""
import argparse
import os

from ..compiler import benchmark_compiler_op, out_directory
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


def bm_MoonBit(results: Results, code_paths, args: argparse.Namespace, op: str, templated: bool):
    lang = 'MoonBit'
    cexe = resolve_compiler_path(args, lang, 'moon')
    if not cexe:
        return

    lang_dir = os.path.abspath(out_directory(lang))
    os.makedirs(lang_dir, exist_ok=True)
    mod_file = os.path.join(lang_dir, "moon.mod")
    if not os.path.exists(mod_file):
        try:
            with open(mod_file, "w") as f:
                f.write('name = "benchmark/test"\nversion = "0.1.0"\n')
        except OSError:
            pass

    if op == 'check':
        cexe_flags = ['check']
        out_flag_and_exe = []
        exec_cmd = False
    elif op == 'build':
        cexe_flags = ['build']
        out_flag_and_exe = []
        exec_cmd = False
    else:
        return

    try:
        version = get_compiler_version(cexe)
    except OSError:
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
    name=Lang('MoonBit'),
    exes=[Exec('moon')],
    extension=FileExt('mbt'),
    int_type=TypeName('Int'),
    runners=[bm_MoonBit],
    ops=('check', 'build'),
    templated_variants=(False,),
    aliases=('moonbit', 'moon'),
    tier=3,
    out_binary=DEFAULT_PROGRAM_NAME,
    versions=[VersionSpec(('moon',), ['version'])],
    func_emitter=make_func_emitter(
        define=lambda fname, _typ, expr, _t: f"fn {fname}(x: Int) -> Int {{\n    {expr}\n}}\n\n",
        leaf=lambda _typ, _t, c: f"(x + {c})",
        chain=lambda _typ, _t, prev, c: f"(x + {prev}(x) + {c})",
    ),
    prefix=lambda _program_name, _t: '',
    main_header=lambda _types, _t: 'fn main {\n',
    var_decl=lambda typ, _t: f"    let mut {typ}_sum : {typ} = 0\n",
    call=lambda i, typ, _t: f"    {typ}_sum = {typ}_sum + {function_name(typ, i)}({i})\n",
    call_terminator='',
    postfix=lambda types: f"    println({types[0]}_sum)\n}}\n",
))
