"""Language support for pony.

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

def bm_Pony(results: Results, code_paths, args: argparse.Namespace, op, templated: bool):
    lang = 'Pony'
    cexe = resolve_compiler_path(args, lang, 'ponyc')
    if not cexe:
        return None
    if op == 'check':
        cexe_flags = ['--pass=verify', '--verbose=0']
        out_flag_and_exe = []
    elif op == 'build':
        cexe_flags = ['--debug', '--verbose=0']
        out_flag_and_exe = ['-o', '.', '-b', out_binary(lang)]
    else:
        return None
    version = get_compiler_version(cexe)
    benchmark_compiler_op(code_paths,
                          out_flag_and_exe=out_flag_and_exe,
                          cexe=cexe,
                          exec_cmd=(op == 'build'),
                          cexe_flags=cexe_flags,
                          args=args,
                          op=op,
                          compiler_version=version,
                          lang=lang,
                          templated=templated,
                          results=results)


PONY_MAX_TOTAL_FUNCS = 1_000
PONY_CAPPED_DIM = 30


def _pony_limits(args: argparse.Namespace) -> list[str]:
    if args.function_count * args.function_depth > PONY_MAX_TOTAL_FUNCS:
        msg = (f"Warning: Capping Pony function count/depth from {args.function_count}x{args.function_depth} "
               f"to {PONY_CAPPED_DIM}x{PONY_CAPPED_DIM} due to ponyc capability checking limits")
        args.function_count = PONY_CAPPED_DIM
        args.function_depth = PONY_CAPPED_DIM
        return [msg]
    return []


def _pony_program_dir(dir_path: str, templated: bool, run_ix: int) -> str:
    # ponyc compiles an entire package directory rather than a single file, so isolate each
    # generated program in its own subdirectory to avoid multiple `actor Main` definitions colliding.
    return os.path.join(dir_path, 'run' + ('_t' if templated else '') + '_' + str(run_ix))


def _pony_build_cmd(cexe, cexe_flags, out_flags, src_name):
    pkg_dir = os.path.dirname(src_name) or '.'
    return [cexe] + cexe_flags + out_flags + [pkg_dir]


register_language(LangSupport(
    name=Lang('Pony'), exes=[Exec('ponyc')], extension=FileExt('pony'), int_type=TypeName('I64'),
    runners=[bm_Pony],
    ops=('check', 'build'),
    limit_args=_pony_limits,
    program_dir=_pony_program_dir,
    build_cmd=_pony_build_cmd,
    func_emitter=make_func_emitter(
        define=lambda fname, typ, expr, t: f"  fun {fname}(x: {typ}): {typ} => {expr}\n"),
    prefix=lambda program_name, t: 'primitive Calc\n',
    main_header=lambda types, t: 'actor Main\n  new create(env: Env) =>\n',
    var_decl=lambda typ, t: f"    var {typ.lower()}_sum: {typ} = 0\n",
    call=lambda i, typ, t: f"    {typ.lower()}_sum = {typ.lower()}_sum + Calc.{function_name(typ, i)}({i})",
    call_terminator='',
    postfix=lambda types: f"    env.exitcode(({types[0].lower()}_sum % 256).i32())\n",
))
