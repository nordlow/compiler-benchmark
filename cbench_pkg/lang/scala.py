"""Language support for scala.

Self-contained block: runner(s) + register_language call. To add a new language,
drop a new module here and it is picked up automatically by the engine.
"""
import argparse
import os
import tempfile
from shutil import which

from ..compiler import benchmark_compiler_op
from ..types import (
    Exec, FileExt, Lang, LangSupport, Results, TypeName, VersionSpec,
    _never_native, function_name, make_func_emitter, register_language,
)
from ..version import get_compiler_version, resolve_compiler_path

SCALA_MAX_TOTAL_FUNCS = 10_000
SCALA_CAPPED_DIM = 100


def _scala_limits(args: argparse.Namespace) -> list[str]:
    if args.function_count * args.function_depth > SCALA_MAX_TOTAL_FUNCS:
        msg = (f"Warning: Capping Scala function count/depth from {args.function_count}x{args.function_depth} "
               f"to {SCALA_CAPPED_DIM}x{SCALA_CAPPED_DIM} due to JVM/constant pool scaling limits")
        args.function_count = SCALA_CAPPED_DIM
        args.function_depth = SCALA_CAPPED_DIM
        return [msg]
    return []


def bm_Scala(results: Results, code_paths, args: argparse.Namespace, op: str, templated: bool):
    lang = 'Scala'
    cexe = resolve_compiler_path(args, lang, 'scalac')
    if not cexe:
        return

    version = get_compiler_version(cexe)
    scala_exe = which('scala') or ('/usr/share/scala3/bin/scala' if os.path.exists('/usr/share/scala3/bin/scala') else 'scala')

    if op == 'check':
        with tempfile.TemporaryDirectory() as tmp_dir:
            benchmark_compiler_op(code_paths,
                                  out_flag_and_exe=['-d', tmp_dir],
                                  cexe=cexe,
                                  exec_cmd=False,
                                  cexe_flags=[],
                                  args=args,
                                  op=op,
                                  compiler_version=version,
                                  lang=lang,
                                  templated=templated,
                                  results=results)
    elif op == 'build':
        benchmark_compiler_op(code_paths,
                              out_flag_and_exe=['-d', '.'],
                              cexe=cexe,
                              exec_cmd=[scala_exe, '-cp', '.'],
                              cexe_flags=[],
                              args=args,
                              op=op,
                              compiler_version=version,
                              lang=lang,
                              templated=templated,
                              results=results)


register_language(LangSupport(
    name=Lang('Scala'),
    exes=[Exec('scalac')],
    extension=FileExt('scala'),
    int_type=TypeName('Long'),
    runners=[bm_Scala],
    ops=('check', 'build'),
    aliases=('scala',),
    tier=3,
    native_output=_never_native,
    versions=[VersionSpec(('scalac',), ['-version'])],
    limit_args=_scala_limits,
    func_emitter=make_func_emitter(
        define=lambda fname, typ, expr, _t: f"  def {fname}(x: {typ}): {typ} = {expr}\n"),
    prefix=lambda _program_name, _t: 'object main {\n',
    main_header=lambda _types, _t: '  def main(args: Array[String]): Unit = {\n',
    var_decl=lambda typ, _t: f"    var {typ}_sum: {typ} = 0L\n",
    call=lambda i, typ, _t: f"    {typ}_sum += {function_name(typ, i)}({i}L)",
    postfix=lambda types: f"    System.exit(if ({types[0]}_sum == 42L) 1 else 0)\n  }}\n}}\n",
))
