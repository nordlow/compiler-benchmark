"""Language support for d.

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

def bm_D(results: Results, code_paths, args: argparse.Namespace, op, templated: bool, use_dips: bool = False):
    lang = 'D'
    d_flags = []
    use_betterC = True
    if use_betterC:
        d_flags += ['-betterC']
    if use_dips:
        d_flags += ['-w', '-dip1008', '-dip1000']

    if op == 'check':
        cexe_flags = ['-o-']
    elif op == 'compile':
        cexe_flags = ['-c']
    elif op == 'build':
        if which('ld.lld') is not None:
            cexe_flags = ["-Xcc=-fuse-ld=lld"]
        elif which('ld.gold') is not None:
            cexe_flags = ["-Xcc=-fuse-ld=gold"]
        else:
            cexe_flags = []
    else:
        return None

    try:
        exes = args.language_exes[lang]
    except KeyError:
        return

    if not exes:
        exes = default_exes(lang)

    for cexe in filter(lambda cexe: which(cexe), exes):
        if not cexe or not which(cexe):
            continue
        if cexe.startswith('dmd'):
            version = get_compiler_version(cexe)
            if os.path.exists('/usr/lib/libmimalloc.so'):
                old_preload = os.environ.get('LD_PRELOAD')
                os.environ['LD_PRELOAD'] = '/usr/lib/libmimalloc.so'
            try:
                benchmark_compiler_op(code_paths=code_paths,
                                      out_flag_and_exe=['-of=' + out_binary(lang)] if op == 'build' else [],
                                      cexe=cexe,
                                      exec_cmd=True,
                                      cexe_flags=d_flags + cexe_flags,
                                      args=args,
                                      op=op,
                                      compiler_version=version,
                                      lang=lang,
                                      templated=templated,
                                      results=results)
            finally:
                if old_preload is None:
                    os.environ.pop('LD_PRELOAD', None)
                else:
                    os.environ['LD_PRELOAD'] = old_preload
        elif cexe.startswith('ldmd2'):
            version = get_compiler_version(cexe)
            benchmark_compiler_op(code_paths=code_paths,
                                  out_flag_and_exe=['-of=' + out_binary(lang)] if op == 'build' else [],
                                  cexe=cexe,
                                  exec_cmd=True,
                                  cexe_flags=d_flags + cexe_flags,
                                  args=args,
                                  op=op,
                                  compiler_version=version,
                                  lang=lang,
                                  templated=templated,
                                  results=results)
        elif cexe.startswith('gdc'):
            cexe_flags = ['-fsyntax-only'] if op == 'check' else []
            version = get_compiler_version(cexe)
            benchmark_compiler_op(code_paths=code_paths,
                                  out_flag_and_exe=['-o' + out_binary(lang)] if op == 'build' else [],
                                  cexe=cexe,
                                  exec_cmd=True,
                                  cexe_flags=cexe_flags,
                                  args=args,
                                  op=op,
                                  compiler_version=version,
                                  lang=lang,
                                  templated=templated,
                                  results=results)


register_language(LangSupport(
    name=Lang('D'), exes=[Exec('dmd'), Exec('ldmd2'), Exec('gdc')], extension=FileExt('d'), int_type=TypeName('long'),
    runners=[bm_D],
    ops=('check', 'compile', 'build'),
    templated_variants=(False, True),
    func_emitter=make_func_emitter(
        define=lambda fname, typ, expr, t: (
            f"{'T' if t else typ} {fname}{'(T)' if t else ''}({'T' if t else typ} x)"
            f" @safe pure nothrow @nogc {{ return {expr}; }}\n"),
    ),
    main_header=lambda types, t: 'extern(C) int main() @safe {\n',
    var_decl=lambda typ, t: f"    {typ} {typ}_sum = 0;\n",
    postfix=lambda types: f"    return cast(int){types[0]}_sum;\n}}\n",
))
