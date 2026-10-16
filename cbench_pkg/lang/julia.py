"""Language support for julia.

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
from ._shared import _ocaml_julia_limits

JULIA_FLAGS = ['--compile=min', '-O0']  # See: https://github.com/JuliaLang/julia/issues/41360#issuecomment-872075102


def bm_Julia(results: Results, code_paths, args: argparse.Namespace, op, templated: bool):
    lang = 'Julia'
    cexe = resolve_compiler_path(args, lang, 'julia')
    if not cexe:
        return None
    if op == 'check':
        cexe_flags = ['-e', 'ex = Meta.parse("begin\\n" * read(ARGS[1], String) * "\\nend"); if isa(ex, Expr) && ex.head === :error; error(string(ex.args[1])); end', '--']
    elif op == 'build':
        cexe_flags = JULIA_FLAGS
    else:
        return None
    version = get_compiler_version(cexe)
    benchmark_compiler_op(code_paths,
                          out_flag_and_exe=[],
                          cexe=cexe,
                          exec_cmd=False,
                          cexe_flags=cexe_flags,
                          args=args,
                          op=op,
                          compiler_version=version,
                          lang=lang,
                          templated=templated,
                          results=results)


register_language(LangSupport(
    name=Lang('Julia'), exes=[Exec('julia')], extension=FileExt('jl'), int_type=TypeName('Int64'),
    runners=[bm_Julia],
    ops=('check', 'build'),
    templated_variants=(False, True),
    tier=3,
    native_output=_never_native,
    limit_args=_ocaml_julia_limits,
    func_emitter=make_func_emitter(
        define=lambda fname, typ, expr, t: (
            f"function {fname}(x{'' if t else '::' + typ}){'' if t else '::' + typ}\n"
            f"    return {expr}\nend;\n")),
    main_header=lambda types, t: f"function main(){'::' + types[0] if t else ''}\n",
    var_decl=lambda typ, t: f"    {typ}_sum{'::' + typ if t else ''} = 0;\n",
    postfix=lambda types: f"    return {types[0]}_sum;\nend\n\nmain()\n",
))
