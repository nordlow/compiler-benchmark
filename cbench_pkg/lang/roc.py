"""Language support for roc.

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

ROC_MAX_TOTAL_FUNCS = 2_500
ROC_CAPPED_DIM = 50


def _roc_limits(args: argparse.Namespace) -> list[str]:
    if args.function_count * args.function_depth > ROC_MAX_TOTAL_FUNCS:
        msg = (f"Warning: Capping Roc function count/depth from {args.function_count}x{args.function_depth} "
               f"to {ROC_CAPPED_DIM}x{ROC_CAPPED_DIM} due to compiler limits")
        args.function_count = ROC_CAPPED_DIM
        args.function_depth = ROC_CAPPED_DIM
        return [msg]
    return []


def bm_Roc(results: Results, code_paths, args: argparse.Namespace, op, templated: bool):
    lang = 'Roc'
    cexe = resolve_compiler_path(args, lang, 'roc')
    if not cexe:
        return None

    if op == 'check':
        cexe_flags = [op]
        out_flag_and_exe = []
    elif op == 'build':
        cexe_flags = [op, '--opt=dev', '--no-cache', '--jobs=1']
        out_flag_and_exe = ['--output=' + out_binary(lang)]
    elif op == 'run':
        cexe_flags = [op]
        out_flag_and_exe = []
    else:
        return None

    version = get_compiler_version(cexe)
    benchmark_compiler_op(
        code_paths,
        out_flag_and_exe=out_flag_and_exe,
        cexe=cexe,
        exec_cmd=(op == 'build'),
        cexe_flags=cexe_flags,
        args=args,
        op=op,
        compiler_version=version,
        lang=lang,
        templated=templated,
        results=results,
    )


def _roc_parse_version(out: str, default: str) -> str | None:
    parts = out.split()
    if 'commit' in parts:
        idx = parts.index('commit')
        if idx + 1 < len(parts):
            return parts[idx + 1].strip(',;:()')
    return parts[1] if len(parts) >= 2 else default


register_language(LangSupport(
    name=Lang('Roc'), exes=[Exec('roc')], extension=FileExt('roc'), int_type=TypeName('I64'),
    runners=[bm_Roc],
    ops=('check', 'build', 'run'),
    limit_args=_roc_limits,
    versions=[VersionSpec(('roc',), ['version'], _roc_parse_version)],
    func_emitter=make_func_emitter(
        define=lambda fname, typ, expr, t: f"{fname} : {typ} -> {typ}\n{fname} = |x| {expr}\n\n",
        chain=lambda typ, t, prev, c: f"x + {prev}(x) + {c}",
    ),
    prefix=lambda program_name, t: 'app [main!] {}\n\n',
    main_header=lambda types, t: 'main! = |_args| {\n',
    var_decl=lambda typ, t: '',
    main_middle=lambda types: f"    _total =\n        0.{types[0]}\n",
    call=lambda i, typ, t: f"        + {function_name(typ, i)}({i})",
    call_terminator='',
    postfix=lambda types: '    Ok({})\n}\n',
))
