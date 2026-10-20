"""Language support for koka.

Self-contained block: runner(s) + register_language call. To add a new language,
drop a new module here and it is picked up automatically by the engine.
"""
import argparse

from ..compiler import benchmark_compiler_op, out_binary
from ..types import (
    Exec, FileExt, Lang, LangSupport, Results, TypeName, VersionSpec,
    _never_native, function_name, make_func_emitter, register_language,
)
from ..version import get_compiler_version, resolve_compiler_path

KOKA_MAX_TOTAL_FUNCS = 2_000
KOKA_CAPPED_DIM = 35


def _koka_limits(args: argparse.Namespace) -> list[str]:
    if args.function_count * args.function_depth > KOKA_MAX_TOTAL_FUNCS:
        msg = (f"Warning: Capping Koka function count/depth from {args.function_count}x{args.function_depth} "
               f"to {KOKA_CAPPED_DIM}x{KOKA_CAPPED_DIM} due to C backend compilation scaling limits")
        args.function_count = KOKA_CAPPED_DIM
        args.function_depth = KOKA_CAPPED_DIM
        return [msg]
    return []


def bm_Koka(results: Results, code_paths, args: argparse.Namespace, op: str, templated: bool):
    lang = 'Koka'
    cexe = resolve_compiler_path(args, lang, 'koka')
    if not cexe:
        return

    version = get_compiler_version(cexe)

    if op == 'check':
        cexe_flags = ['--check', '-v0', '--ccopts=-w']
        out_flag_and_exe = []
        exec_cmd = False
    elif op == 'build':
        cexe_flags = ['-v0', '--ccopts=-w']
        out_flag_and_exe = ['-o', out_binary(lang)]
        exec_cmd = True
    else:
        return

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


def _koka_parse_version(out: str, default: str) -> str | None:
    parts = out.split()
    for p in parts:
        if p.startswith('v') or any(c.isdigit() for c in p):
            return p.lstrip('v')
    return default


register_language(LangSupport(
    name=Lang('Koka'),
    exes=[Exec('koka')],
    extension=FileExt('kk'),
    int_type=TypeName('int'),
    runners=[bm_Koka],
    ops=('check', 'build'),
    aliases=('koka',),
    tier=3,
    native_output=_never_native,
    versions=[VersionSpec(('koka',), ['--version'], _koka_parse_version)],
    limit_args=_koka_limits,
    source_filename=lambda program_name, _templated, _run_ix, ext: f"{program_name}.{ext}",
    func_emitter=make_func_emitter(
        define=lambda fname, typ, expr, _t: f"fun {fname}(x : {typ}) : {typ} {{ {expr} }}\n"),
    prefix=lambda _program_name, _t: 'module main\n\n',
    main_header=lambda _types, _t: 'pub fun main() : int {\n  var sum := 0\n',
    var_decl=lambda _typ, _t: "",
    call=lambda i, typ, _t: f"  sum := sum + {function_name(typ, i)}({i})\n",
    call_terminator="",
    postfix=lambda _types: "  if (sum == 42) then 1 else 0\n}\n",
))
