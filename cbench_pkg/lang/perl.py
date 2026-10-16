"""Language support for perl.

Self-contained block: runner(s) + register_language call. To add a new language,
drop a new module here and it is picked up automatically by the engine.

Perl has no separate compile-to-file step (no `perlcc` shipped here), so it is
treated like a script language: `perl -c` performs a syntax check and `perl
program.pl` compiles + runs in one step (mirroring the Node.js/Elixir model).
"""
import argparse
import re

from ..types import (
    Lang, Exec, FileExt, TypeName, LangSupport, register_language,
    make_func_emitter, function_name, _never_native,
    VersionSpec, DEFAULT_PROGRAM_NAME,
)
from ..version import get_compiler_version
from ..compiler import benchmark_compiler_op, resolve_compiler_path


def _perl_version(output: str, default: str) -> str | None:
    """Extract the Perl version from `perl -v` output.

    Output contains a line like::

        This is perl 5, version 42, subversion 3 (v5.42.3*) built for ...

    The default parser would return the first digit-led token (`5`), so we parse
    the version/subversion pair instead.
    """
    m = re.search(r"version\s+(\d+),\s+subversion\s+(\d+)", output)
    if m:
        return f"{m.group(1)}.{m.group(2)}"
    return None


def bm_Perl(results: Results, code_paths: list, args: argparse.Namespace, op: str, templated: bool):
    lang = 'Perl'

    cexe = resolve_compiler_path(args, lang, 'perl')
    if not cexe:
        return None

    if op == 'check':
        cexe_flags = ['-c']
        out_flag_and_exe = []
        exec_cmd = False
    elif op == 'build':
        # `perl program.pl` compiles to opcodes and runs in one step.
        cexe_flags = []
        out_flag_and_exe = []
        exec_cmd = [cexe]
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


PERL_MAX_TOTAL_FUNCS = 22_500
PERL_CAPPED_DIM = 150


def _perl_limits(args: argparse.Namespace) -> list[str]:
    if args.function_count * args.function_depth > PERL_MAX_TOTAL_FUNCS:
        msg = (f"Warning: Capping Perl function count/depth from "
               f"{args.function_count}x{args.function_depth} to "
               f"{PERL_CAPPED_DIM}x{PERL_CAPPED_DIM} due to perl scaling limits")
        args.function_count = PERL_CAPPED_DIM
        args.function_depth = PERL_CAPPED_DIM
        return [msg]
    return []


register_language(LangSupport(
    name=Lang('Perl'), exes=[Exec('perl')], extension=FileExt('pl'), int_type=TypeName('int'),
    runners=[bm_Perl],
    ops=('check', 'build'),
    aliases=('pl',),
    tier=3,
    out_binary=DEFAULT_PROGRAM_NAME + '.pl',
    native_output=_never_native,
    versions=[VersionSpec(('perl',), ['-v'], parse=_perl_version)],
    limit_args=_perl_limits,
    func_emitter=make_func_emitter(
        define=lambda fname, typ, expr, t: f"sub {fname} {{ my ($x) = @_; return {expr}; }}\n",
        leaf=lambda typ, t, c: f"$x + {c}",
        chain=lambda typ, t, prev, c: f"$x + {prev}($x) + {c}",
    ),
    prefix=lambda program_name, t: "use strict;\nuse warnings;\n\n",
    main_header=lambda types, t: "",
    var_decl=lambda typ, t: f"my ${typ}_sum = 0;\n",
    call=lambda i, typ, t: f"${typ}_sum = ${typ}_sum + {function_name(typ, i)}({i});\n",
    call_terminator='',
    postfix=lambda types: f"${types[0]}_sum = ${types[0]}_sum;\nexit(0);\n",
))
