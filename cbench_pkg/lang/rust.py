"""Language support for rust.

Self-contained block: runner(s) + register_language call. To add a new language,
drop a new module here and it is picked up automatically by the engine.
"""
import argparse
import copy
import os
import shutil
import tempfile
import subprocess as sp
from shutil import which

from ..types import (
    Lang, Exec, FileExt, TypeName, LangSupport, register_language,
    make_func_emitter, plain_call, function_name, lisp_let_middle,
    _default_leaf, _default_chain, _no_limits, _no_text, _defs_then_header,
    _always_native, _never_native, default_exes, VersionSpec, DEFAULT_PROGRAM_NAME,
)
from ..version import resolve_compiler_path, find_compiler_versions, get_compiler_version
from ..compiler import benchmark_compiler_op, build_compiler_cmd, out_directory, out_binary

RUSTC_NO_WARNINGS_FLAGS = ['-A', 'warnings']  # disable warnings for `rustc`
RUSTC_FLAGS = []  # set to `RUSTC_NO_WARNINGS_FLAGS` to disable warnings

# Requires: rustup component add rustc-codegen-cranelift-preview --toolchain nightly
# Call: cargo +nightly rustc -- -Zcodegen-backend=cranelift
RUSTC_NIGHTLY_FLAGS = ['-Z', 'threads=1', '-Zcodegen-backend=cranelift']  # See: https://blog.rust-lang.org/2023/11/09/parallel-rustc.html


def set_rustup_channel(channel):
    with sp.Popen(['rustup', 'default', channel],
                  stdout=sp.PIPE,
                  stderr=sp.PIPE) as proc:
        proc.communicate()


def rust_flags(channel):
    flags = RUSTC_FLAGS
    return flags


def bm_Rust(results: Results, code_paths, args: argparse.Namespace, op, templated: bool):
    lang = 'Rust'

    rustup_exe = which('rustup')
    if rustup_exe:
        rustup_channels = ['stable', 'nightly']
    else:
        rustup_channels = [None]

    try:
        exes = args.language_exes[lang]
    except KeyError:
        return
    if not exes:
        exes = default_exes(lang)

    for channel in rustup_channels:
        if rustup_exe is not None:
            set_rustup_channel(channel)

        for cexe in exes:
            version = get_compiler_version(cexe)
            if op == 'check':
                check_args = ['--emit=metadata']
                out_flag_and_exe = []
            elif op == 'build':
                out_flag_and_exe = ['-o', out_binary(lang)]
            else:
                continue
            cexe_flags = ([] if op == 'build' else check_args) + rust_flags(channel)
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
    name=Lang('Rust'), exes=[Exec('rustc')], extension=FileExt('rs'), int_type=TypeName('i64'),
    runners=[bm_Rust],
    ops=('check', 'build'),
    templated_variants=(False, True),
    func_emitter=make_func_emitter(
        define=lambda fname, typ, expr, t: (
            f"fn {fname}<T: Copy + Add<Output = T>>(x: T) -> T {{ {expr} }}\n" if t
            else f"fn {fname}(x: {typ}) -> {typ} {{ {expr} }}\n"),
        leaf=lambda typ, t, c: ("x" if t else f"x + {c}"),
        chain=lambda typ, t, prev, c: (f"x + {prev}(x)" if t else f"x + {prev}(x) + {c}"),
    ),
    prefix=lambda program_name, t: 'use std::process::exit;\n' + ('use std::ops::Add;\n' if t else ''),
    main_header=lambda types, t: 'fn main() {\n',
    var_decl=lambda typ, t: f"    let mut {typ}_sum : {typ} = 0;\n",
    postfix=lambda types: f"    exit(({types[0]}_sum % 4294967296) as i32);\n}}\n",
))
