"""Language support for go.

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

def bm_Go_using_go(results: Results, code_paths, args: argparse.Namespace, op, templated: bool):
    lang = 'Go'
    cexe = resolve_compiler_path(args, lang, 'go')
    if not cexe:
        return

    version = get_compiler_version(cexe)
    if op == 'build':
        cexe_flags = ['build']
        out_flag_and_exe = ['-o', out_binary(lang)]
        exec_cmd = True
    elif op == 'check':
        cexe_flags = ['vet']
        out_flag_and_exe = []
        exec_cmd = False
    else:
        return None

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


def bm_Go_using_gccgo(results: Results, code_paths, args: argparse.Namespace, op, templated: bool):
    lang = 'Go'
    for cexe in find_compiler_versions(args, lang, 'gccgo'):
        benchmark_compiler_op(code_paths, [], cexe, True, [] if op == 'build' else ['-fsyntax-only', '-S'],
                              args, op, get_compiler_version(cexe), lang, templated, results)


def bm_Go(results: Results, code_paths, args: argparse.Namespace, op, templated: bool):
    bm_Go_using_go(results, code_paths, args, op, templated)
    bm_Go_using_gccgo(results, code_paths, args, op, templated)


def _go_parse_version(out: str, default: str) -> str | None:
    parts = out.split()
    if len(parts) >= 3 and parts[2].startswith('go'):
        return parts[2][2:].split('~')[0].split('ubuntu')[0]
    return None


register_language(LangSupport(
    name=Lang('Go'), exes=[Exec('go'), Exec('gccgo')], extension=FileExt('go'), int_type=TypeName('int64'),
    runners=[bm_Go],
    ops=('check', 'build'),
    templated_variants=(False, True),
    versions=[VersionSpec(('go',), ['version'], _go_parse_version)],
    func_emitter=make_func_emitter(
        define=lambda fname, typ, expr, t: f"func {fname}(x {typ}) {typ} {{ return {expr} }}\n"),
    prefix=lambda program_name, t: f"package {program_name};\n// import (\"os\")\n\n",
    main_header=lambda types, t: 'func main() {\n',
    var_decl=lambda typ, t: f"    var {typ}_sum {typ} = 0;\n",
    postfix=lambda types: f"    // os.Exit(int({types[0]}_sum));\n}}\n",
))
