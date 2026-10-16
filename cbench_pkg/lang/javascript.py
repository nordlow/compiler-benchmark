"""Language support for javascript (Node.js).

Self-contained block: runner(s) + register_language call. To add a new language,
drop a new module here and it is picked up automatically by the engine.
"""
import argparse

from ..types import (
    Lang, Exec, FileExt, TypeName, LangSupport, register_language,
    make_func_emitter, function_name, _never_native, default_exes,
    VersionSpec, DEFAULT_PROGRAM_NAME,
)
from ..version import resolve_compiler_path, get_compiler_version
from ..compiler import benchmark_compiler_op, out_binary


def bm_JavaScript(results: Results, code_paths: list, args: argparse.Namespace, op: str, templated: bool):
    lang = 'JavaScript'

    exes = args.language_exes.get(lang) or default_exes(lang)

    for cexe_name in exes:
        cexe = resolve_compiler_path(args, lang, cexe_name)
        if not cexe:
            continue

        if op == 'check':
            # `node --check <file>`: syntax check without executing.
            cexe_flags = ['--check']
            out_flag_and_exe = []
            exec_cmd = False
        elif op == 'build':
            # Running the script parses + JIT-compiles + executes in one step.
            cexe_flags = []
            out_flag_and_exe = []
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


register_language(LangSupport(
    name=Lang('JavaScript'), exes=[Exec('node')], extension=FileExt('js'), int_type=TypeName('int'),
    runners=[bm_JavaScript],
    ops=('check', 'build'),
    aliases=('node', 'js'),
    tier=3,
    out_binary=DEFAULT_PROGRAM_NAME + '.js',
    native_output=_never_native,
    versions=[VersionSpec(('node',), ['--version'])],
    func_emitter=make_func_emitter(
        define=lambda fname, typ, expr, t: f"function {fname}(x) {{ return {expr}; }}\n",
    ),
    main_header=lambda types, t: 'function main() {\n',
    var_decl=lambda typ, t: f"    let {typ}_sum = 0;\n",
    call=lambda i, typ, t: f"    {typ}_sum += {function_name(typ, i)}({i});",
    call_terminator='',
    postfix=lambda types: f"    void {types[0]}_sum;\n    process.exit(0);\n}}\n\nmain();\n",
))
