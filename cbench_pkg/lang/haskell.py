"""Language support for haskell.

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

HASKELL_MAX_TOTAL_FUNCS = 10_000
HASKELL_CAPPED_DIM = 100


def _haskell_limits(args: argparse.Namespace) -> list[str]:
    if args.function_count * args.function_depth > HASKELL_MAX_TOTAL_FUNCS:
        msg = (f"Warning: Capping Haskell function count/depth from {args.function_count}x{args.function_depth} "
               f"to {HASKELL_CAPPED_DIM}x{HASKELL_CAPPED_DIM} due to GHC scaling limits")
        args.function_count = HASKELL_CAPPED_DIM
        args.function_depth = HASKELL_CAPPED_DIM
        return [msg]
    return []


def bm_Haskell(results: Results, code_paths, args: argparse.Namespace, op, templated: bool):
    lang = 'Haskell'
    cexe = resolve_compiler_path(args, lang, 'ghc')
    if not cexe:
        return None

    if op == 'check':
        cexe_flags = ['-fno-code', '-v0', '-dynamic']
        out_flag_and_exe = []
    elif op == 'build':
        cexe_flags = ['-O0', '-v0', '-dynamic']
        out_flag_and_exe = ['-o', out_binary(lang)]
    else:
        return None

    try:
        version = get_compiler_version(cexe)
    except Exception:
        version = 'unknown'

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


register_language(LangSupport(
    name=Lang('Haskell'), exes=[Exec('ghc')], extension=FileExt('hs'), int_type=TypeName('Int64'),
    runners=[bm_Haskell],
    ops=('check', 'build'),
    templated_variants=(False, True),
    aliases=('ghc',),
    tier=3,
    limit_args=_haskell_limits,
    func_emitter=make_func_emitter(
        define=lambda fname, typ, expr, t: (
            f"{fname} :: Num a => a -> a\n{fname} x = {expr}\n" if t
            else f"{fname} :: {typ} -> {typ}\n{fname} x = {expr}\n"),
        chain=lambda typ, t, prev, c: f"x + {prev} x + {c}",
    ),
    prefix=lambda program_name, t: ("module Main where\n\n"
                                    "import Data.Int (Int64)\n"
                                    "import Data.IORef (newIORef, modifyIORef', readIORef)\n"
                                    "import System.Exit (exitWith, ExitCode(..))\n\n"),
    main_header=lambda types, t: 'main :: IO ()\nmain = do\n',
    var_decl=lambda typ, t: f"    {typ.lower()}_sum <- newIORef (0 :: {typ})\n",
    call=lambda i, typ, t: f"    modifyIORef' {typ.lower()}_sum (\\s -> s + {function_name(typ, i)} {i})",
    call_terminator='',
    postfix=lambda types: (f"    s <- readIORef {types[0].lower()}_sum\n"
                           f"    let code = fromIntegral (s `mod` 256)\n"
                           f"    exitWith (if code == 0 then ExitSuccess else ExitFailure code)\n"),
))
