"""Language support for erlang (OTP).

Self-contained block: runner(s) + register_language call. To add a new language,
drop a new module here and it is picked up automatically by the engine.

Erlang compiles each source file to a `.beam` bytecode file with `erlc` and runs
it with `erl -noshell -s <module> main -s init halt`. Erlang requires the module
name to match the source file name, so every generated program uses a fixed
module name `main` placed in its own per-run subdirectory (mirroring Pony), with
`erlc -o <lang_dir>` placing the resulting `main.beam` where `erl` can find it.
"""
import argparse
import os
from shutil import which

from ..types import (
    Lang, Exec, FileExt, TypeName, LangSupport, register_language,
    make_func_emitter, function_name, _never_native,
    VersionSpec, DEFAULT_PROGRAM_NAME,
)
from ..version import get_compiler_version
from ..compiler import benchmark_compiler_op, out_directory


def _erlang_program_dir(dir_path: str, templated: bool, run_ix: int) -> str:
    # Isolate each generated program in its own subdirectory so each can use the
    # fixed module name `main` (Erlang requires module name == source file name)
    # without colliding across repetitions.
    return os.path.join(dir_path, 'run' + ('_t' if templated else '') + '_' + str(run_ix))


def bm_Erlang(results: Results, code_paths: list, args: argparse.Namespace, op: str, templated: bool):
    lang = 'Erlang'
    lang_dir = out_directory(lang)

    erlc = which('erlc')
    if not erlc:
        return None

    # Version is read from the OTP emulator (`erl`), which prints `emulator
    # version <erts>` and exits cleanly under `-noshell`.
    version = get_compiler_version('erl')

    # `erlc -o <lang_dir> <src>` writes `main.beam` into lang_dir regardless of
    # which per-run subdirectory the source lives in.
    out_flag_and_exe = ['-o', lang_dir]

    if op == 'compile':
        exec_cmd = False
    elif op == 'build':
        # Run the beam with the lang_dir on the code path. The trailing beam
        # path (appended by run_target_binary) is ignored by `erl -s ...`.
        exec_cmd = ['erl', '-noshell', '-pa', lang_dir,
                    '-s', 'main', 'main', '-s', 'init', 'halt']
    else:
        return None

    benchmark_compiler_op(code_paths,
                          out_flag_and_exe=out_flag_and_exe,
                          cexe=erlc,
                          exec_cmd=exec_cmd,
                          cexe_flags=[],
                          args=args,
                          op=op,
                          compiler_version=version,
                          lang=lang,
                          templated=templated,
                          results=results)


ERLANG_MAX_TOTAL_FUNCS = 40_000
ERLANG_CAPPED_DIM = 200


def _erlang_limits(args: argparse.Namespace) -> list[str]:
    # The beam loader and the emulator scale poorly on deeply nested call trees
    # with very large synthetic function counts.
    if args.function_count * args.function_depth > ERLANG_MAX_TOTAL_FUNCS:
        msg = (f"Warning: Capping Erlang function count/depth from "
               f"{args.function_count}x{args.function_depth} to "
               f"{ERLANG_CAPPED_DIM}x{ERLANG_CAPPED_DIM} due to beam scaling limits")
        args.function_count = ERLANG_CAPPED_DIM
        args.function_depth = ERLANG_CAPPED_DIM
        return [msg]
    return []


register_language(LangSupport(
    name=Lang('Erlang'), exes=[Exec('erlc')], extension=FileExt('erl'), int_type=TypeName('int'),
    runners=[bm_Erlang],
    ops=('compile', 'build'),
    aliases=('erl',),
    tier=3,
    out_binary=DEFAULT_PROGRAM_NAME + '.beam',
    native_output=_never_native,
    versions=[VersionSpec(('erl',), ['-noshell', '-version'])],
    limit_args=_erlang_limits,
    program_dir=_erlang_program_dir,
    source_filename=lambda program_name, templated, run_ix, ext: f"{program_name}.{ext}",
    func_emitter=make_func_emitter(
        define=lambda fname, typ, expr, t: f"{fname}(X) -> {expr}.\n",
        leaf=lambda typ, t, c: f"X + {c}",
        chain=lambda typ, t, prev, c: f"X + {prev}(X) + {c}",
    ),
    prefix=lambda program_name, t: "-module(main).\n-export([main/0]).\n\n",
    main_header=lambda types, t: "main() ->\n",
    var_decl=lambda typ, t: f"    {typ.capitalize()}_sum = 0,\n",
    call=lambda i, typ, t: f"    {typ.capitalize()}_sum = {typ.capitalize()}_sum + {function_name(typ, i)}({i}),",
    call_terminator='',
    postfix=lambda types: "    halt(0).\n",
))
