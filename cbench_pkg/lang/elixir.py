"""Language support for elixir.

Self-contained block: runner(s) + register_language call. To add a new language,
drop a new module here and it is picked up automatically by the engine.

Elixir scripts (`.exs`) are compiled to BEAM bytecode and executed in one step
by the `elixir` command, so there is no separate compile-to-file step like
there is for Erlang. This mirrors the Node.js model: `build` runs `elixir
main.exs` (compile + run) and `run` re-runs it.

Elixir does not expose a syntax-only check, so only `build` is offered.
"""
import argparse
from shutil import which

from ..types import (
    Lang, Exec, FileExt, TypeName, LangSupport, register_language,
    make_func_emitter, function_name, _never_native,
    VersionSpec, DEFAULT_PROGRAM_NAME,
)
from ..version import get_compiler_version
from ..compiler import benchmark_compiler_op


def _elixir_version(output: str, default: str) -> str | None:
    """Extract the Elixir version from `elixir --version` output.

    Output looks like::

        Erlang/OTP 29 [...]
        Elixir 1.20.4 (compiled with Erlang/OTP 29)

    The first digit-led token is the OTP release (`29`), so we look for the
    `Eli<|reserved_205943|>` line specifically.
    """
    for line in output.splitlines():
        line = line.strip()
        if line.startswith("Elixir "):
            parts = line.split()
            if len(parts) > 1:
                return parts[1]
    return None


def bm_Elixir(results: Results, code_paths: list, args: argparse.Namespace, op: str, templated: bool):
    lang = 'Elixir'

    cexe = which('elixir')
    if not cexe:
        return None

    # Version is read from `elixir --version` via a custom parser.
    version = get_compiler_version('elixir')

    if op == 'build':
        # `elixir main.exs` compiles to BEAM and runs in one step.
        cexe_flags = []
        out_flag_and_exe = []
        exec_cmd = [cexe]
    else:
        return None

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


ELIXIR_MAX_TOTAL_FUNCS = 22_500
ELIXIR_CAPPED_DIM = 150


def _elixir_limits(args: argparse.Namespace) -> list[str]:
    if args.function_count * args.function_depth > ELIXIR_MAX_TOTAL_FUNCS:
        msg = (f"Warning: Capping Elixir function count/depth from "
               f"{args.function_count}x{args.function_depth} to "
               f"{ELIXIR_CAPPED_DIM}x{ELIXIR_CAPPED_DIM} due to BEAM scaling limits")
        args.function_count = ELIXIR_CAPPED_DIM
        args.function_depth = ELIXIR_CAPPED_DIM
        return [msg]
    return []


register_language(LangSupport(
    name=Lang('Elixir'), exes=[Exec('elixir')], extension=FileExt('exs'), int_type=TypeName('int'),
    runners=[bm_Elixir],
    ops=('build',),
    aliases=('ex', 'exs'),
    tier=3,
    out_binary=DEFAULT_PROGRAM_NAME + '.exs',
    native_output=_never_native,
    versions=[VersionSpec(('elixir',), ['--version'], parse=_elixir_version)],
    limit_args=_elixir_limits,
    func_emitter=make_func_emitter(
        define=lambda fname, typ, expr, t: f"  def {fname}(x), do: {expr}\n",
        leaf=lambda typ, t, c: f"x + {c}",
        chain=lambda typ, t, prev, c: f"x + {prev}(x) + {c}",
    ),
    prefix=lambda program_name, t: "defmodule Main do\n",
    main_header=lambda types, t: "  def main do\n",
    var_decl=lambda typ, t: f"    int_sum = 0\n",
    call=lambda i, typ, t: f"    int_sum = int_sum + {function_name(typ, i)}({i})\n",
    call_terminator='',
    postfix=lambda types: "    _ = int_sum\n    System.halt(0)\n  end\nend\n\nMain.main()\n",
))
