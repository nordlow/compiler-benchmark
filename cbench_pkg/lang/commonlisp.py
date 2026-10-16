"""Language support for commonlisp.

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

def bm_CommonLisp(results: Results, code_paths: list, args: argparse.Namespace, op: str, templated: bool):
    lang = 'Common-Lisp'
    cexe = resolve_compiler_path(args, lang, 'sbcl')
    if not cexe:
        return None

    if op == 'check':
        with tempfile.NamedTemporaryFile(suffix='.check.fasl') as tmp_file:
            cexe_flags = [
                '--noinform',
                '--non-interactive',
                '--no-sysinit',
                '--no-userinit',
                '--eval',
                f'(progn (setf *error-output* (make-broadcast-stream) *compile-verbose* nil *compile-print* nil) (declaim (sb-ext:muffle-conditions style-warning sb-ext:compiler-note)) (multiple-value-bind (out warn fail) (compile-file "{{}}" :output-file "{tmp_file.name}" :verbose nil :print nil) (when fail (sb-ext:exit :code 1))))',
            ]
            version = get_compiler_version(cexe)
            return benchmark_compiler_op(code_paths,
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
    elif op == 'compile':
        cexe_flags = [
            '--noinform',
            '--non-interactive',
            '--no-sysinit',
            '--no-userinit',
            '--eval',
            '(progn (setf *error-output* (make-broadcast-stream) *compile-verbose* nil *compile-print* nil) (declaim (sb-ext:muffle-conditions style-warning sb-ext:compiler-note)) (multiple-value-bind (out warn fail) (compile-file "{}" :output-file "main.fasl" :verbose nil :print nil) (when fail (sb-ext:exit :code 1))))',
        ]
        out_flag_and_exe = []
        exec_cmd = False
    elif op == 'build':
        cexe_flags = [
            '--noinform',
            '--non-interactive',
            '--no-sysinit',
            '--no-userinit',
            '--eval',
            '(progn (setf *error-output* (make-broadcast-stream) *compile-verbose* nil *compile-print* nil) (declaim (sb-ext:muffle-conditions style-warning sb-ext:compiler-note)) (multiple-value-bind (out warn fail) (compile-file "{}" :verbose nil :print nil) (if fail (sb-ext:exit :code 1) (progn (load out :verbose nil :print nil) (when (probe-file "main") (delete-file "main")) (sb-ext:save-lisp-and-die "main" :toplevel (quote cl-user::main) :executable t)))))',
        ]
        out_flag_and_exe = []
        exec_cmd = True
    else:
        return None

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


def _sbcl_build_cmd(cexe, cexe_flags, out_flags, src_name):
    # the `{}` placeholder inside the --eval form is the source file name
    formatted_flags = [f.format(src_name) if '{}' in f else f for f in cexe_flags]
    return [cexe] + formatted_flags + out_flags


register_language(LangSupport(
    name=Lang('Common-Lisp'), exes=[Exec('sbcl')], extension=FileExt('lisp'), int_type=TypeName('int'),
    runners=[bm_CommonLisp],
    ops=('check', 'compile', 'build'),
    aliases=('commonlisp', 'common-lisp', 'lisp', 'sbcl'),
    tier=3,
    build_cmd=_sbcl_build_cmd,
    func_emitter=make_func_emitter(
        define=lambda fname, typ, expr, t: f"(defun {fname} (x) {expr})\n",
        leaf=lambda typ, t, c: f"(+ x {c})",
        chain=lambda typ, t, prev, c: f"(+ x ({prev} x) {c})",
    ),
    prefix=lambda program_name, t: '(in-package :cl-user)\n\n',
    main_header=lambda types, t: '(defun main ()\n',
    main_middle=lisp_let_middle,
    call=lambda i, typ, t: f"    (setf {typ}_sum (+ {typ}_sum ({function_name(typ, i)} {i})))",
    call_terminator='',
    postfix=lambda types: f"    (sb-ext:exit :code (mod {types[0]}_sum 256))))\n",
))
