"""Language support for emacslisp.

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

EMACS_LISP_MAX_TOTAL_FUNCS = 10_000
EMACS_LISP_CAPPED_DIM = 100


def _emacs_lisp_limits(args: argparse.Namespace) -> list[str]:
    if args.function_count * args.function_depth > EMACS_LISP_MAX_TOTAL_FUNCS:
        msg = (f"Warning: Capping Emacs-Lisp function count/depth from {args.function_count}x{args.function_depth} "
               f"to {EMACS_LISP_CAPPED_DIM}x{EMACS_LISP_CAPPED_DIM} due to Emacs bytecode compiler and recursion limits")
        args.function_count = EMACS_LISP_CAPPED_DIM
        args.function_depth = EMACS_LISP_CAPPED_DIM
        return [msg]
    return []


def _emacs_parse_version(out: str, default: str) -> str | None:
    parts = out.split()
    return parts[2] if len(parts) >= 3 else default


def _emacs_lisp_build_cmd(cexe, cexe_flags, out_flags, src_name):
    src_clean = src_name.replace('\\', '/')
    if any('{}' in f for f in cexe_flags):
        formatted_flags = [f.format(src_clean) if '{}' in f else f for f in cexe_flags]
        return [cexe] + formatted_flags + out_flags
    return [cexe] + cexe_flags + out_flags + [src_clean]


def bm_EmacsLisp(results: Results, code_paths: list, args: argparse.Namespace, op: str, templated: bool):
    lang = 'Emacs-Lisp'
    cexe = resolve_compiler_path(args, lang, 'emacs')
    if not cexe:
        return None

    target_elc = out_binary(lang)
    version = get_compiler_version(cexe)

    if op == 'check':
        target_check_elc = "main.check.elc"
        eval_expr = (
            f'(progn '
            f'(require \'bytecomp) '
            f'(setq byte-compile-warnings nil inhibit-message t) '
            f'(setq byte-compile-dest-file-function (lambda (_) "{target_check_elc}")) '
            f'(unless (byte-compile-file "{{}}") (kill-emacs 1)))'
        )
        cexe_flags = ['-Q', '--batch', '--eval', eval_expr]
        try:
            benchmark_compiler_op(code_paths,
                                  out_flag_and_exe=[],
                                  cexe=cexe,
                                  exec_cmd=False,
                                  cexe_flags=cexe_flags,
                                  args=args,
                                  op=op,
                                  compiler_version=version,
                                  lang=lang,
                                  templated=templated,
                                  results=results)
        finally:
            check_file_path = os.path.join(out_directory(lang), target_check_elc)
            if os.path.exists(check_file_path):
                try:
                    os.remove(check_file_path)
                except OSError:
                    pass
    elif op == 'compile':
        eval_expr = (
            f'(progn '
            f'(require \'bytecomp) '
            f'(setq byte-compile-warnings nil inhibit-message t) '
            f'(setq byte-compile-dest-file-function (lambda (_) "{target_elc}")) '
            f'(unless (byte-compile-file "{{}}") (kill-emacs 1)))'
        )
        cexe_flags = ['-Q', '--batch', '--eval', eval_expr]
        benchmark_compiler_op(code_paths,
                              out_flag_and_exe=[],
                              cexe=cexe,
                              exec_cmd=False,
                              cexe_flags=cexe_flags,
                              args=args,
                              op=op,
                              compiler_version=version,
                              lang=lang,
                              templated=templated,
                              results=results)
    elif op == 'build':
        eval_expr = (
            f'(progn '
            f'(require \'bytecomp) '
            f'(setq byte-compile-warnings nil inhibit-message t) '
            f'(setq byte-compile-dest-file-function (lambda (_) "{target_elc}")) '
            f'(unless (byte-compile-file "{{}}") (kill-emacs 1)))'
        )
        cexe_flags = ['-Q', '--batch', '--eval', eval_expr]
        benchmark_compiler_op(code_paths,
                              out_flag_and_exe=[],
                              cexe=cexe,
                              exec_cmd=[cexe, '-Q', '--batch', '-l'],
                              cexe_flags=cexe_flags,
                              args=args,
                              op=op,
                              compiler_version=version,
                              lang=lang,
                              templated=templated,
                              results=results)
    elif op == 'run':
        cexe_flags = ['-Q', '--batch', '-l', '{}']
        benchmark_compiler_op(code_paths,
                              out_flag_and_exe=[],
                              cexe=cexe,
                              exec_cmd=False,
                              cexe_flags=cexe_flags,
                              args=args,
                              op=op,
                              compiler_version=version,
                              lang=lang,
                              templated=templated,
                              results=results)
    else:
        return None


register_language(LangSupport(
    name=Lang('Emacs-Lisp'),
    exes=[Exec('emacs')],
    extension=FileExt('el'),
    int_type=TypeName('int'),
    runners=[bm_EmacsLisp],
    ops=('check', 'compile', 'build', 'run'),
    aliases=('elisp', 'emacs-lisp', 'el'),
    tier=3,
    out_binary=DEFAULT_PROGRAM_NAME + '.elc',
    native_output=_never_native,
    versions=[VersionSpec(('emacs',), ['--version'], _emacs_parse_version)],
    limit_args=_emacs_lisp_limits,
    build_cmd=_emacs_lisp_build_cmd,
    func_emitter=make_func_emitter(
        define=lambda fname, typ, expr, t: f"(defun {fname} (x)\n  {expr})\n",
        leaf=lambda typ, t, c: f"(+ x {c})",
        chain=lambda typ, t, prev, c: f"(+ x ({prev} x) {c})",
    ),
    prefix=lambda program_name, t: (
        ";; -*- lexical-binding: t; -*-\n"
        "(setq max-lisp-eval-depth 50000)\n"
        "(setq max-specpdl-size 50000)\n\n"
    ),
    main_header=lambda types, t: '(defun main ()\n',
    main_middle=lisp_let_middle,
    call=lambda i, typ, t: f"    (setq {typ}_sum (+ {typ}_sum ({function_name(typ, i)} {i})))",
    call_terminator='',
    postfix=lambda types: (
        f"    {types[0]}_sum))\n\n"
        "(main)\n"
        "(kill-emacs 0)\n"
    ),
))
