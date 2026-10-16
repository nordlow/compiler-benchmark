"""Language support for vox.

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


def bm_Vox(results: Results, code_paths, args: argparse.Namespace, op, templated: bool):
    lang = 'Vox'
    cexe = resolve_compiler_path(args, lang, 'vox')
    if not cexe:
        return

    if op == 'check':
        cexe_flags = ['--check-only']
        out_flag_and_exe = []
    elif op == 'compile':
        return None
    elif op == 'build':
        cexe_flags = []
        out_flag_and_exe = ['--of=' + out_binary(lang)]
    else:
        return None

    benchmark_compiler_op(code_paths,
                          out_flag_and_exe=out_flag_and_exe,
                          cexe=cexe,
                          exec_cmd=True,
                          cexe_flags=cexe_flags,
                          args=args,
                          op=op,
                          compiler_version='master',
                          lang=lang,
                          templated=templated,
                          results=results)


if False:  # disabled for now until I get this to work
    register_language(LangSupport(
        name=Lang('Vox'), exes=[Exec('vox')], extension=FileExt('vx'), int_type=TypeName('i64'),
        runners=[bm_Vox],
        ops=('check', 'build'),
        templated_variants=(False, True),
        versions=[VersionSpec(('vox',), fixed='master')],
        func_emitter=make_func_emitter(
            define=lambda fname, typ, expr, t: (
                f"{'T' if t else typ} {fname}{'[T]' if t else ''}({'T' if t else typ} x) {{ return {expr}; }}\n"),
            chain=lambda typ, t, prev, c: (f"x + {prev}[{typ}](x) + {c}" if t else f"x + {prev}(x) + {c}"),
        ),
        prefix=lambda program_name, t: (
            "enum u32 stdin = 0;\n"
            "enum u32 stdout = 1;\n"
            "enum u32 stderr = 2;\n"
            "\n"
            "@extern(syscall, 60)\n"
            "void exit(i32 error_code);\n"
            "\n"
            "@extern(syscall, 1)\n"
            "void sys_write(u32 fd, u8* buf, u64 count);\n"
            "\n"
            "void write(u32 fd, u8[] data) {\n"
            "\tsys_write(fd, data.ptr, data.length);\n"
            "}\n"),
        main_header=lambda types, t: 'i32 main() {\n',
        var_decl=lambda typ, t: f"    {typ} {typ}_sum = 0;\n",
        call=lambda i, typ, t: f"    {typ}_sum += {function_name(typ, i)}{'[' + typ + ']' if t else ''}({i})",
        postfix=lambda types: "    exit(0);\n    return 0;\n}\n",
    ))
