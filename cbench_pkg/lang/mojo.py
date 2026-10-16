"""Language support for mojo.

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

def bm_Mojo(results: Results, code_paths, args: argparse.Namespace, op, templated: bool):
    lang = 'Mojo'
    cexe = resolve_compiler_path(args, lang, 'mojo')
    if not cexe:
        return None

    version = get_compiler_version(cexe)
    benchmark_compiler_op(code_paths,
                          out_flag_and_exe=['-o', out_binary(lang)],
                          cexe=cexe,
                          exec_cmd=True,
                          cexe_flags=['build', '-O0'],
                          args=args,
                          op=op,
                          compiler_version=version,
                          lang=lang,
                          templated=templated,
                          results=results)


register_language(LangSupport(
    name=Lang('Mojo'), exes=[Exec('mojo')], extension=FileExt('mojo'), int_type=TypeName('Int'),
    runners=[bm_Mojo],
    ops=('build',),
    func_emitter=make_func_emitter(
        define=lambda fname, typ, expr, t: f"fn {fname}(x: {typ}) -> {typ}: return {expr}\n"),
    main_header=lambda types, t: 'fn main() -> int:\n',
    var_decl=lambda typ, t: f"    var {typ}_sum: {typ} = 0;\n",
    postfix=lambda types: (f"    sys.exit(int({types[0]}_sum) & 0xFFFFFFFF)\n\n"
                           f"if __name__ == '__main__':\n    main()\n"),
))
