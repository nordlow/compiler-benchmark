"""Language support for scheme.

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

def bm_Scheme(results: Results, code_paths, args: argparse.Namespace, op, templated: bool):
    lang = 'Scheme'
    cexe = resolve_compiler_path(args, lang, 'chez') or resolve_compiler_path(args, lang, 'scheme')
    if not cexe:
        return None

    version = get_compiler_version(cexe)
    out_target = out_binary(lang)

    if op == 'check':
        cexe_flags = ['-q']
        # Skip shebang line if present (ASCII 35 = '#', 10 = newline), then read and expand AST
        stdin_input = (
            '(reset-handler abort) '
            '(call-with-input-file "main_{}.scm" '
            '(lambda (p) '
            '(unless (eof-object? (peek-char p)) '
            '(when (eqv? (char->integer (peek-char p)) 35) '
            '(let skip () (let ([c (read-char p)]) (unless (or (eof-object? c) (eqv? (char->integer c) 10)) (skip)))))) '
            '(let f () (let ([x (read p)]) (unless (eof-object? x) (expand x) (f))))))'
        )
        exec_cmd = False
    elif op == 'compile':
        cexe_flags = ['-q']
        stdin_input = '(reset-handler abort) (compile-file "main_{}.scm")'
        exec_cmd = False
    elif op == 'build':
        cexe_flags = ['-q']
        stdin_input = f'(reset-handler abort) (compile-script "main_{{}}.scm" "{out_target}")'
        exec_cmd = [cexe, '--script']
    else:
        return None

    benchmark_compiler_op(code_paths,
                          out_flag_and_exe=[],
                          cexe=cexe,
                          exec_cmd=exec_cmd,
                          cexe_flags=cexe_flags,
                          args=args,
                          op=op,
                          compiler_version=version,
                          lang=lang,
                          templated=templated,
                          results=results,
                          stdin_input=stdin_input)


register_language(LangSupport(
    name=Lang('Scheme'), exes=[Exec('chez'), Exec('scheme')], extension=FileExt('scm'), int_type=TypeName('int'),
    runners=[bm_Scheme],
    ops=('check', 'compile', 'build'),
    aliases=('chez',),
    tier=3,
    native_output=_never_native,
    versions=[VersionSpec(('scheme', 'chez'), ['--version'], lambda out, default: out)],
    func_emitter=make_func_emitter(
        define=lambda fname, typ, expr, t: f"(define ({fname} x) {expr})\n",
        leaf=lambda typ, t, c: f"(+ x {c})",
        chain=lambda typ, t, prev, c: f"(+ x ({prev} x) {c})",
    ),
    prefix=lambda program_name, t: '#!/usr/bin/env scheme --script\n\n',
    main_header=lambda types, t: '(define (main)\n',
    main_middle=lisp_let_middle,
    call=lambda i, typ, t: f"    (set! {typ}_sum (+ {typ}_sum ({function_name(typ, i)} {i})))",
    call_terminator='',
    postfix=lambda types: f"    {types[0]}_sum))\n(exit (main))\n",
))
