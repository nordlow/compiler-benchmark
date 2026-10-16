"""Language support for zig.

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

zig_no_llvm_build_flags = ['-fno-llvm', '-fno-lld', '-fno-clang']


def bm_Zig(results: Results, code_paths, args: argparse.Namespace, op, templated: bool):
    lang = 'Zig'
    cexe = resolve_compiler_path(args, lang, 'zig')
    if not cexe:
        return
    if op == 'ast-check':
        cexe_flags = ['ast-check']
        out_flag_and_exe = []
    elif op == 'check':
        cexe_flags = ['build-obj', '-fno-emit-bin'] + zig_no_llvm_build_flags
        out_flag_and_exe = []
    elif op == 'compile':
        cexe_flags = ['build-obj'] + zig_no_llvm_build_flags
        out_flag_and_exe = []
    elif op == 'build':
        cexe_flags = ['build-exe'] + zig_no_llvm_build_flags
        out_flag_and_exe = ['--name', out_binary(lang)]
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


register_language(LangSupport(
    name=Lang('Zig'), exes=[Exec('zig')], extension=FileExt('zig'), int_type=TypeName('i64'),
    runners=[bm_Zig],
    ops=('ast-check', 'check', 'compile', 'build'),
    templated_variants=(False, True),
    versions=[VersionSpec(('zig',), ['version'])],
    func_emitter=make_func_emitter(
        define=lambda fname, typ, expr, t: (
            f"fn {fname}(comptime T: type, x: T) T {{ return {expr}; }}\n" if t
            else f"fn {fname}(x: {typ}) {typ} {{ return {expr}; }}\n"),
        chain=lambda typ, t, prev, c: (f"x + {prev}({typ}, x) + {c}" if t else f"x + {prev}(x) + {c}"),
    ),
    main_header=lambda types, t: 'pub fn main() void {\n',
    var_decl=lambda typ, t: f"    var {typ}_sum: {typ} = 0;\n",
    call=lambda i, typ, t: (f"    {typ}_sum += {function_name(typ, i)}({typ}, {i})" if t else plain_call(i, typ, t)),
    postfix=lambda types: "\n}\n",
))
