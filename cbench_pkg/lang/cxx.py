"""Language support for cxx.

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
from ..compiler import benchmark_compiler_op, build_compiler_cmd, out_directory, out_binary, bm_C_and_Cxx_using_gcc, bm_C_and_Cxx_using_clang

register_language(LangSupport(
    name=Lang('C++'), exes=[Exec('g++'), Exec('clang++')], extension=FileExt('cpp'), int_type=TypeName('long'),
    runners=[
        lambda r, cp, a, op, t: bm_C_and_Cxx_using_gcc(r, 'C++', cp, a, op, t),
        lambda r, cp, a, op, t: bm_C_and_Cxx_using_clang(r, 'C++', cp, a, op, t),
    ],
    ops=('check', 'compile', 'build'),
    templated_variants=(False, True),
    func_emitter=make_func_emitter(
        define=lambda fname, typ, expr, t: (
            f"template<typename T> T {fname}(T x) {{ return {expr}; }}\n" if t
            else f"{typ} {fname}({typ} x) {{ return {expr}; }}\n")),
    main_header=lambda types, t: 'int main(void) {\n',
    var_decl=lambda typ, t: f"    {typ} {typ}_sum = 0;\n",
    postfix=lambda types: f"    return {types[0]}_sum;\n}}\n",
))
