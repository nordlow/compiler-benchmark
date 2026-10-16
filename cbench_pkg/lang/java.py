"""Language support for java.

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

def bm_Java(results: Results, code_paths, args: argparse.Namespace, op, templated: bool):
    lang = 'Java'
    cexe = resolve_compiler_path(args, lang, 'javac')
    if not cexe:
        return None
    cexe_flags = ['-Xdiags:verbose']
    if op == 'check':
        cexe_flags += ['-proc:only', '-nowarn']
    version = get_compiler_version(cexe)
    benchmark_compiler_op(code_paths,
                          out_flag_and_exe=[],
                          cexe=cexe,
                          exec_cmd=[which('java'), '-classpath', '.'],
                          cexe_flags=cexe_flags,
                          args=args,
                          op=op,
                          compiler_version=version,
                          lang=lang,
                          templated=templated,
                          results=results)


JAVA_MAX_TOTAL_FUNCS = 10_000
JAVA_CAPPED_DIM = 100


def _java_limits(args: argparse.Namespace) -> list[str]:
    # JVM class format limit: the constant pool cannot exceed 65535 entries per class
    if args.function_count * args.function_depth > JAVA_MAX_TOTAL_FUNCS:
        msg = (f"Warning: Capping Java function count/depth from {args.function_count}x{args.function_depth} "
               f"to {JAVA_CAPPED_DIM}x{JAVA_CAPPED_DIM} due to JVM constant pool limits")
        args.function_count = JAVA_CAPPED_DIM
        args.function_depth = JAVA_CAPPED_DIM
        return [msg]
    return []


register_language(LangSupport(
    name=Lang('Java'), exes=[Exec('javac')], extension=FileExt('java'), int_type=TypeName('long'),
    runners=[bm_Java],
    ops=('check', 'build'),
    tier=3,
    native_output=_never_native,
    versions=[VersionSpec(('javac',), ['-version'])],
    limit_args=_java_limits,
    func_emitter=make_func_emitter(
        define=lambda fname, typ, expr, t: f"    static {typ} {fname}({typ} x) {{ return {expr}; }}\n"),
    prefix=lambda program_name, t: 'class HelloWorld {\n',
    main_header=lambda types, t: '    public static void main(String args[]) {\n',
    var_decl=lambda typ, t: f"        {typ} {typ}_sum = 0;\n",
    call=lambda i, typ, t: f"        {typ}_sum += {function_name(typ, i)}({i})",
    postfix=lambda types: f"        System.exit({types[0]}_sum == 42 ? 1 : 0);\n    }}\n}}\n",
))
