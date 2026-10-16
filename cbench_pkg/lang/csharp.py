"""Language support for csharp.

Self-contained block: runner(s) + register_language call. To add a new language,
drop a new module here and it is picked up automatically by the engine.
"""
import argparse
import copy
import os
import subprocess as sp
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

def bm_CSharp_using_mcs(results: Results, code_paths, args: argparse.Namespace, op, templated: bool):
    lang = 'C#'
    cexe = resolve_compiler_path(args, lang, 'mcs')
    if not cexe:
        return

    cexe_flags = ['-target:exe']
    try:
        version_output = sp.run([cexe, '--version'], stdout=sp.PIPE, stderr=sp.STDOUT).stdout.decode('utf-8')
        version = version_output.split()[4]
    except (IndexError, sp.CalledProcessError, Exception):
        version = "unknown"

    mono_exe = which('mono')
    target_bin = os.path.abspath(os.path.join(out_directory(lang), out_binary(lang)))
    if op == 'check':
        with tempfile.NamedTemporaryFile(suffix='.check_tmp') as tmp_file:
            benchmark_compiler_op(code_paths,
                                  out_flag_and_exe=['-out:' + tmp_file.name],
                                  cexe=cexe,
                                  exec_cmd=[mono_exe] if mono_exe else True,
                                  cexe_flags=cexe_flags,
                                  args=args,
                                  op=op,
                                  compiler_version=version,
                                  lang=lang,
                                  templated=templated,
                                  results=results)
    else:
        benchmark_compiler_op(code_paths,
                              out_flag_and_exe=['-out:' + target_bin],
                              cexe=cexe,
                              exec_cmd=[mono_exe] if mono_exe else True,
                              cexe_flags=cexe_flags,
                              args=args,
                              op=op,
                              compiler_version=version,
                              lang=lang,
                              templated=templated,
                              results=results)


def bm_CSharp_using_csc(results: Results, code_paths, args: argparse.Namespace, op, templated: bool):
    lang = 'C#'
    cexe = resolve_compiler_path(args, lang, 'csc')
    if not cexe:
        return

    cexe_flags = ['-target:exe']
    version = get_compiler_version(cexe)
    mono_exe = which('mono')

    if op == 'check':
        with tempfile.NamedTemporaryFile(suffix='.check_tmp') as tmp_file:
            benchmark_compiler_op(code_paths,
                                  out_flag_and_exe=['-out:' + tmp_file.name],
                                  cexe=cexe,
                                  exec_cmd=[mono_exe] if mono_exe else True,
                                  cexe_flags=cexe_flags + ['-refonly'],
                                  args=args,
                                  op=op,
                                  compiler_version=version,
                                  lang=lang,
                                  templated=templated,
                                  results=results)
    else:
        benchmark_compiler_op(code_paths,
                              out_flag_and_exe=['-out:' + out_binary(lang)],
                              cexe=cexe,
                              exec_cmd=[mono_exe] if mono_exe else True,
                              cexe_flags=cexe_flags,
                              args=args,
                              op=op,
                              compiler_version=version,
                              lang=lang,
                              templated=templated,
                              results=results)


register_language(LangSupport(
    name=Lang('C#'), exes=[Exec('mcs'), Exec('csc')],  # mcs: Mono C# 6.12.0.200, csc: Microsoft Visual C#
    extension=FileExt('cs'), int_type=TypeName('long'),
    runners=[bm_CSharp_using_mcs, bm_CSharp_using_csc],
    ops=('check', 'build'),
    tier=3,
    native_output=_never_native,
    versions=[VersionSpec(('csc',), ['-version'])],
    func_emitter=make_func_emitter(
        define=lambda fname, typ, expr, t: f"    static {typ} {fname}({typ} x) {{ return {expr}; }}\n"),
    prefix=lambda program_name, t: 'using System;\n\npublic class HelloWorld {\n',
    main_header=lambda types, t: '    public static void Main(string[] args) {\n',
    var_decl=lambda typ, t: f"        {typ} {typ}_sum = 0;\n",
    call=lambda i, typ, t: f"        {typ}_sum += {function_name(typ, i)}({i})",
    postfix=lambda types: f"        Environment.Exit({types[0]}_sum == 42 ? 1 : 0);\n    }}\n}}\n",
))
