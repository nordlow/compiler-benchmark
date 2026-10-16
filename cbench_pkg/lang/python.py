"""Language support for python.

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
    _always_native, _never_native, default_exes, VersionSpec, DEFAULT_PROGRAM_NAME,
)
from ..version import resolve_compiler_path, find_compiler_versions, get_compiler_version
from ..compiler import benchmark_compiler_op, build_compiler_cmd, out_directory, out_binary

def bm_Python(results: Results, code_paths: list, args: argparse.Namespace, op: str, templated: bool):
    lang = 'Python'
    target_pyc = out_binary(lang)

    exes = args.language_exes.get(lang) or default_exes(lang)

    for cexe_name in exes:
        cexe = resolve_compiler_path(args, lang, cexe_name)
        if not cexe:
            continue

        if op == 'check':
            cexe_flags = ['-c', 'import sys; compile(open(sys.argv[1], "rb").read(), sys.argv[1], "exec")']
            out_flag_and_exe = []
            exec_cmd = False
        elif op == 'compile':
            cexe_flags = ['-O', '-c', 'import py_compile, sys; py_compile.compile(sys.argv[2], cfile=sys.argv[1], doraise=True)']
            out_flag_and_exe = [target_pyc]
            exec_cmd = False
        elif op == 'build':
            cexe_flags = ['-O', '-c', 'import py_compile, sys; py_compile.compile(sys.argv[2], cfile=sys.argv[1], doraise=True)']
            out_flag_and_exe = [target_pyc]
            exec_cmd = [cexe, '-S', '-O']
        else:
            continue

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
    name=Lang('Python'), exes=[Exec('python3'), Exec('python3.15'), Exec('pypy3')],
    extension=FileExt('py'), int_type=TypeName('Int'),
    runners=[bm_Python],
    ops=('check', 'compile', 'build'),
    templated_variants=(False, True),
    tier=3,
    out_binary=DEFAULT_PROGRAM_NAME + '.pyc',
    native_output=_never_native,
    func_emitter=make_func_emitter(
        define=lambda fname, typ, expr, t: (
            f"def {fname}(x: int) -> int:\n    return {expr}\n\n" if t
            else f"def {fname}(x):\n    return {expr}\n\n")),
    prefix=lambda program_name, t: 'import sys\n\n',
    main_header=lambda types, t: 'def main() -> int:\n' if t else 'def main():\n',
    var_decl=lambda typ, t: f"    {typ}_sum: {typ} = 0\n" if t else f"    {typ}_sum = 0\n",
    postfix=lambda types: (f"    sys.exit(int({types[0]}_sum) & 0xFFFFFFFF)\n\n"
                           f"if __name__ == '__main__':\n    main()\n"),
))
