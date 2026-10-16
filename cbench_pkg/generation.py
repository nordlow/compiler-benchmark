"""
Test-program source code generation.

Generates the synthetic arithmetic translation units (call chains of `add_*`
functions) that are fed to each compiler. The per-language layout (prefix,
function emitter, main header/vars/calls/postfix, section ordering) is supplied
by the language's `LangSupport`.
"""

import io
import os
from timeit import default_timer as timer

from .types import (
    LangSupport,
    DEFAULT_PROGRAM_NAME,
    function_name,
    lang_support,
)


def _default_program_dir(dir_path: str, templated: bool, run_ix: int) -> str:
    return dir_path


def _default_source_filename(program_name: str, templated: bool, run_ix: int, ext: str) -> str:
    return f"{program_name}{'_t' if templated else ''}_{run_ix}.{ext}"


def _defs_then_header(write_header, write_defs):
    write_defs()
    write_header()


def generate_function_definitions(spec: LangSupport, types: list, args, sink, templated: bool):
    write = sink.write
    func_count = args.function_count
    func_depth = args.function_depth
    from .types import RAND_STR_POOL, RAND_POOL_MASK, RANDOMIZE_FLAG
    rand_pool = RAND_STR_POOL
    mask = RAND_POOL_MASK
    rand_idx = 0
    for typ in types:
        emitter = spec.func_emitter(typ, templated, func_depth)
        for findex in range(func_count):
            chunk = []
            for fheight in range(func_depth):
                nconst = rand_pool[rand_idx & mask] if RANDOMIZE_FLAG else str(findex)
                rand_idx += 1
                chunk.append(emitter(findex, fheight, nconst))
            chunk.append('\n')
            write(''.join(chunk))
        write('\n')


def generate_test_program_source(spec: LangSupport,
                                 args,
                                 templated: bool,
                                 *,
                                 order_sections=_defs_then_header) -> str:
    """Generate the synthetic source code text for `spec`."""
    program_name = DEFAULT_PROGRAM_NAME
    types = [spec.int_type]
    buf = io.StringIO()
    buf.write(spec.prefix(program_name, templated))

    order_sections(
        lambda: buf.write(spec.main_header(types, templated)),
        lambda: generate_function_definitions(spec, types, args, buf, templated),
    )

    for typ in types:
        buf.write(spec.var_decl(typ, templated))

    buf.write(spec.main_middle(types))

    for typ in types:
        for findex in range(args.function_count):
            buf.write(spec.call(findex, typ, templated) + spec.call_terminator + '\n')

    buf.write(spec.postfix(types))
    return buf.getvalue()


def generate_test_program_file(lang: str,
                               args,
                               templated: bool,
                               run_ix,
                               *,
                               program_dir=None,
                               source_filename=None,
                               order_sections=None):
    """Write the generated program to a file and return its path."""
    if program_dir is None:
        from .types import _default_program_dir as program_dir
    if source_filename is None:
        from .types import _default_source_filename as source_filename
    if order_sections is None:
        order_sections = _defs_then_header

    spec = lang_support(lang)
    program_name = DEFAULT_PROGRAM_NAME
    # Lazy import to avoid a circular import (compiler imports generation).
    from .compiler import out_directory
    dir_path = program_dir(out_directory(lang), templated, run_ix)
    os.makedirs(dir_path, exist_ok=True)
    path = os.path.join(dir_path, source_filename(program_name, templated, run_ix, spec.extension))

    start = timer()
    content = generate_test_program_source(spec, args, templated, order_sections=order_sections)

    with open(path, 'w') as sink:
        sink.write(content)
    dur = timer() - start
    if getattr(args, 'verbose', False):
        print(f'- Generating {path} took {dur:1.3f} seconds ({lang})')

    return path
