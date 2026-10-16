"""Language support for hare.

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

def bm_Hare(results: Results, code_paths, args: argparse.Namespace, op, templated: bool):
    lang = 'Hare'
    cexe = resolve_compiler_path(args, lang, 'hare')
    if not cexe:
        return None

    try:
        version = get_compiler_version(cexe)
    except Exception:
        version = 'unknown'

    cache_dir = os.path.join(tempfile.gettempdir(), f'hare_cache_{op}')
    shutil.rmtree(cache_dir, ignore_errors=True)
    os.environ['HARECACHE'] = cache_dir

    if op == 'check':
        with tempfile.NamedTemporaryFile(suffix='.check_tmp') as tmp_file:
            benchmark_compiler_op(code_paths,
                                  out_flag_and_exe=['-o', tmp_file.name],
                                  cexe=cexe,
                                  exec_cmd=False,
                                  cexe_flags=['build'],
                                  args=args,
                                  op=op,
                                  compiler_version=version,
                                  lang=lang,
                                  templated=templated,
                                  results=results)
    elif op == 'build':
        benchmark_compiler_op(code_paths,
                              out_flag_and_exe=['-o', out_binary(lang)],
                              cexe=cexe,
                              exec_cmd=True,
                              cexe_flags=['build'],
                              args=args,
                              op=op,
                              compiler_version=version,
                              lang=lang,
                              templated=templated,
                              results=results)
    else:
        return None


register_language(LangSupport(
    name=Lang('Hare'), exes=[Exec('hare')], extension=FileExt('ha'), int_type=TypeName('i64'),
    runners=[bm_Hare],
    ops=('check', 'build'),
    versions=[VersionSpec(('hare',), ['version'])],
    func_emitter=make_func_emitter(
        define=lambda fname, typ, expr, t: f"fn {fname}(x: {typ}) {typ} = {{ return {expr}; }};\n"),
    prefix=lambda program_name, t: 'use os;\n\n',
    main_header=lambda types, t: 'export fn main() void = {\n',
    var_decl=lambda typ, t: f"    let {typ}_sum: {typ} = 0;\n",
    postfix=lambda types: f"    os::exit(({types[0]}_sum % 256): int);\n}};\n",
))
