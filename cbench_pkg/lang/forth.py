"""Language support for Forth (gforth).

Self-contained block: runner(s) + register_language call. To add a new language,
drop a new module here and it is picked up automatically by the engine.
"""
import argparse
import copy
import os
import shlex
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
from ..compiler import benchmark_compiler_op, out_binary


FORTH_MAX_TOTAL_FUNCS = 10_000
FORTH_CAPPED_DIM = 100

# gforth is an interpreter: sources are compiled into an in-memory dictionary and
# the only persistent artifact is a snapshot of that dictionary ("image"). The
# stock engine cannot make a *relocatable* image (ASLR moves the load address), so
# we use the gforthmi helper, which produces one via a pair of images + comp-image.
GFORTHMI = which('gforthmi')


def _forth_build_cmd(cexe: str, cexe_flags: list, out_flags: list, src_name: str) -> list:
    """gforth loads the source file before any trailing `-e` flags."""
    parts = list(cexe_flags) + [src_name] + list(out_flags)
    if parts and parts[0] == cexe:
        return parts
    # Image ops run through gforthmi, whose comp-image step prints progress; silence it.
    cmd = ' '.join(shlex.quote(p) for p in parts)
    return ['sh', '-c', f'{cmd} >/dev/null 2>&1']


def _forth_limits(args: argparse.Namespace) -> list[str]:
    if args.function_count * args.function_depth > FORTH_MAX_TOTAL_FUNCS:
        msg = (f"Warning: Capping Forth function count/depth from {args.function_count}x{args.function_depth} "
               f"to {FORTH_CAPPED_DIM}x{FORTH_CAPPED_DIM} due to Forth dictionary limits")
        args.function_count = FORTH_CAPPED_DIM
        args.function_depth = FORTH_CAPPED_DIM
        return [msg]
    return []


def _forth_leaf(typ: str, templated: bool, c: str) -> str:
    # Forth: ( x -- x )  x + c  =>  {c} +
    return f"{c} +"


def _forth_chain(typ: str, templated: bool, prev: str, c: str) -> str:
    # Forth: x + prev(x) + c  =>  dup {prev} + {c} +
    return f"dup {prev} + {c} +"


def bm_Forth_using_gforth(results: Results, code_paths, args: argparse.Namespace, op, templated: bool):
    lang = 'Forth'
    cexe = resolve_compiler_path(args, lang, 'gforth')
    if not cexe:
        return

    image = out_binary(lang)
    if op == 'check':
        # Compile the source into the dictionary, then leave.
        cexe_flags = [cexe]
        out_flag_and_exe = ['-e', 'bye']
        exec_cmd = False
    elif op in ('compile', 'build'):
        # `gforthmi <image> <source>`: compile a relocatable Forth image.
        if not GFORTHMI:
            return None
        cexe_flags = [GFORTHMI, image]
        out_flag_and_exe = []
        # The image installs a `'cold` hook that runs `main` on startup, so the
        # run step is just loading the image.
        exec_cmd = [cexe, '-i'] if op == 'build' else False
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


register_language(LangSupport(
    name=Lang('Forth'), exes=[Exec('gforth')],
    extension=FileExt('fs'), int_type=TypeName('int'),
    runners=[bm_Forth_using_gforth],
    ops=('check', 'compile', 'build'),
    templated_variants=(False,),
    aliases=('forth',),
    tier=3,
    out_binary=DEFAULT_PROGRAM_NAME + '.fi',
    native_output=_never_native,
    build_cmd=_forth_build_cmd,
    versions=[VersionSpec(('gforth',), ['--version'])],
    limit_args=_forth_limits,
    func_emitter=make_func_emitter(
        define=lambda fname, typ, expr, t: f": {fname} ( x -- x ) {expr} ;\n",
        leaf=_forth_leaf,
        chain=_forth_chain,
    ),
    main_header=lambda types, t: ": main ( -- ) 0 ",
    var_decl=lambda typ, t: "",
    main_middle=lambda types: "",
    call=lambda i, typ, t: f"{i} {function_name(typ, i)} +",
    call_terminator='',
    # Define the program but defer execution to image startup: `main` is run by a
    # `'cold` hook, so `check`/`compile` only build and `build` runs on image load.
    postfix=lambda types: "cr . ;\n:noname ( -- ) defers 'cold main bye ; is 'cold\n",
))
