"""Language support for lua.

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
    _always_native, _never_native, default_exes, VersionSpec, DEFAULT_PROGRAM_NAME,
)
from ..version import resolve_compiler_path, find_compiler_versions, get_compiler_version
from ..compiler import benchmark_compiler_op, build_compiler_cmd, out_directory, out_binary

def bm_Lua(results: Results, code_paths: list, args: argparse.Namespace, op: str, templated: bool):
    lang = 'Lua'
    target_luac = out_binary(lang)

    exes = args.language_exes.get(lang) or default_exes(lang)

    for cexe_name in exes:
        cexe = resolve_compiler_path(args, lang, cexe_name)
        if not cexe:
            continue

        if op == 'check':
            cexe_flags = ['-b']
            out_flag_and_exe = [os.devnull]
            exec_cmd = False
        elif op == 'compile':
            cexe_flags = ['-b']
            out_flag_and_exe = [target_luac]
            exec_cmd = False
        elif op == 'build':
            cexe_flags = ['-b']
            out_flag_and_exe = [target_luac]
            exec_cmd = [cexe]
        else:
            continue

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


LUA_MAX_TOTAL_FUNCS = 20_000
LUA_CAPPED_DIM = 150


def _lua_limits(args: argparse.Namespace) -> list[str]:
    # LuaJIT limit: chunk constant table limit is 65536
    if args.function_count * args.function_depth > LUA_MAX_TOTAL_FUNCS:
        msg = (f"Warning: Capping Lua function count/depth from {args.function_count}x{args.function_depth} "
               f"to {LUA_CAPPED_DIM}x{LUA_CAPPED_DIM} due to LuaJIT chunk constant limits")
        args.function_count = LUA_CAPPED_DIM
        args.function_depth = LUA_CAPPED_DIM
        return [msg]
    return []


def _luajit_build_cmd(cexe, cexe_flags, out_flags, src_name):
    # `luajit -b <src> <out>`: the source comes before the output file
    return [cexe] + cexe_flags + [src_name] + out_flags


register_language(LangSupport(
    name=Lang('Lua'), exes=[Exec('luajit')], extension=FileExt('lua'), int_type=TypeName('int'),
    runners=[bm_Lua],
    ops=('check', 'compile', 'build'),
    aliases=('luajit',),
    tier=3,
    out_binary=DEFAULT_PROGRAM_NAME + '.luac',
    native_output=_never_native,
    versions=[VersionSpec(('luajit',), ['-v'])],
    limit_args=_lua_limits,
    build_cmd=_luajit_build_cmd,
    func_emitter=make_func_emitter(
        define=lambda fname, typ, expr, t: f"function {fname}(x) return {expr} end\n"),
    main_header=lambda types, t: 'function main()\n',
    var_decl=lambda typ, t: f"    local {typ}_sum = 0\n",
    call=lambda i, typ, t: f"    {typ}_sum = {typ}_sum + {function_name(typ, i)}({i})",
    call_terminator='',
    postfix=lambda types: f"    os.exit(math.floor({types[0]}_sum) % 256)\nend\n\nmain()\n",
))
