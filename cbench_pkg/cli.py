"""
Command-line interface and benchmark driver.

Parses arguments, discovers compilers, builds the task graph (one task per
language/operation/templated-variant/runner), executes it in a multiprocessing
pool pinned to CPU cores, and renders the Markdown result tables.
"""

import argparse
import copy
import importlib
import os
import random
import sys
import tempfile
import multiprocessing as mp
import threading
import builtins
import atexit
import shutil
import time
import pkgutil
from datetime import datetime

from cpu_topology import get_available_cpus

from .types import (
    Lang,
    Exec,
    Op,
    ValuesMode,
    DEFAULT_FUNCTION_COUNT,
    DEFAULT_FUNCTION_DEPTH,
    DEFAULT_RUN_COUNT,
    DEFAULT_SAMPLE_RATE,
    DEFAULT_TIMEOUT,
    LANGUAGES,
    build_lang_aliases,
    lang_support,
    DEFAULT_OPERATIONS,
    VERSIONS,
)
from .version import resolve_compiler_path
from .compiler import _worker_init, _run_task, _merge_results
from .reporting import markdown_table, table_titles, markdown_header
from .progress import (
    _make_locked_print,
    _progress_monitor,
    _clear_status,
    _supports_tree_progress,
    MONITOR_JOIN_TIMEOUT_SEC,
)
from .generation import generate_test_program_source

# Import every language module so its `register_language(...)` call fires and
# populates the `LANGUAGES` registry. Doing this at module load time (rather
# than only inside main()) keeps the registry populated in worker processes
# too (important when multiprocessing uses the "spawn" start method).
import cbench_pkg.lang as _lang_pkg
for _m in pkgutil.iter_modules(_lang_pkg.__path__):
    if _m.name.startswith("_"):
        continue
    importlib.import_module(f"cbench_pkg.lang.{_m.name}")


# --- module-level state set by main() ---
ROOT_PATH = None
MAIN_PID = os.getpid()

ADAPTIVE_FAST_DUR_THRESHOLD = 1.0
ADAPTIVE_FAST_RUN_COUNT = 3
ADAPTIVE_SLOW_DUR_THRESHOLD = 3.0
ADAPTIVE_SLOW_RUN_COUNT = 2

HOMOGENEOUS_CPU_RESERVE = 2
TEMP_DIR_BASE = "/tmp"
TEMP_DIR_PREFIX = "generated_"

RANDOMIZE_FLAG = True

if RANDOMIZE_FLAG:
    random.seed(str(datetime.now()))


def install_missing_modules():
    for mod in ('psutil', 'prettytable'):
        try:
            importlib.import_module(mod)
        except ModuleNotFoundError:
            print(f"Installing missing module: {mod}...")
            import subprocess as sp
            sp.check_call([sys.executable, "-m", "pip", "install", mod])
            print(f"Module {mod} installed successfully.")


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--languages', '--langs', type=str,
                        default=None,
                        help='Languages (optionally combined with compilers) to benchmark separated by comma. For instance --languages=C:tcc,D:dmd,D:gdc,D:ldmd2.')

    parser.add_argument('--path', type=str,
                        default=None,
                        help='Path in which to look for compilers')

    parser.add_argument('--operations', '--ops', type=str,
                        default=','.join(str(o) for o in DEFAULT_OPERATIONS),
                        help='Operations to perform separated by comma')

    parser.add_argument('--ast-check', action='store_true',
                        help='Include AST syntax check (e.g. zig ast-check) in check operations')

    parser.add_argument('--function-count', '--fc', type=int,
                        default=DEFAULT_FUNCTION_COUNT,
                        help='Number of functions generated and called')

    parser.add_argument('--function-depth', '--fd', type=int,
                        default=DEFAULT_FUNCTION_DEPTH,
                        help='Function call depth')

    parser.add_argument('--sample-rate', '--sr', type=int,
                        default=DEFAULT_SAMPLE_RATE,
                        help='Rate of memory usage sampling. Unit is samples per second.')

    parser.add_argument('--timeout', type=float, default=DEFAULT_TIMEOUT,
                        help=f'Per-compilation timeout in seconds (default: {DEFAULT_TIMEOUT})')

    parser.add_argument('--run-count', '--rc', type=int,
                        default=DEFAULT_RUN_COUNT,
                        help='Number of runs for each compilation')

    parser.add_argument('--values', '--val', type=str,
                        choices=['absolute', 'relative', 'both'],
                        default='absolute',
                        help='Whether to display absolute, relative, or both numeric values in the table.')

    parser.add_argument('--relative', '--rel', action='store_true',
                        help='Display relative numeric values (shortcut for --values=relative).')

    parser.add_argument('--highlight-min', '--hl', action='store_true',
                        help='Color- and bold-highlight the smallest (best) raw value in each column, '
                             'in whichever --values mode is selected (absolute, relative, or both).')

    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose progress logging.')

    parser.add_argument("--sort", "--sort-by", type=str,
                        choices=["total", "name", "lang", "check", "compile", "build", "run",
                                 "check-rss", "build-rss", "output-size", "size"],
                        default="total",
                        help="Column to sort table results by (default: total [Total=Build+Run]).")

    parser.add_argument("--sort-reverse", "--sort-desc", action="store_true",
                        help="Sort table results in descending order instead of ascending.")

    parser.add_argument("--progress", "--progress-format", type=str,
                        choices=["auto", "tree", "line", "none"],
                        default="auto",
                        help="Progress monitor format: auto (tree on capable terminals, line otherwise), tree, line, or none.")

    parser.add_argument('--print-code', '--print-generated-code', '--show-code', '--pc',
                        action='store_true',
                        help='Print the resulting generated code (defaults --fc=2, --fd=2, --rc=1).')

    args = parser.parse_args()
    if args.relative:
        args.values = ValuesMode.RELATIVE
    else:
        args.values = ValuesMode(args.values)
    install_missing_modules()

    lang_aliases = build_lang_aliases()

    def normalize_lang_spec(spec: str) -> str:
        name, sep, exes = spec.partition(":")
        canonical = lang_aliases.get(name.lower(), Lang(name.capitalize()))
        return f"{canonical}{sep}{exes}" if sep else canonical

    user_specified_languages = args.languages is not None
    raw_languages = args.languages if user_specified_languages else ','.join(LANGUAGES.keys())
    args.languages = [
        normalize_lang_spec(spec.strip())
        for spec in raw_languages.split(',')
        if spec.strip()
    ]
    args.language_exes = {}
    for language_exes_spec in args.languages:
        split = language_exes_spec.split(':')
        if len(split) == 2:
            language = split[0]
            exes = [e.strip() for e in split[1].split(',') if e.strip()]
        else:
            language = split[0]
            exes = []
        if language not in LANGUAGES:
            print('Warning: Ignoring unsupported language ' + language)
            continue

        candidate_exes = exes if exes else [str(e) for e in LANGUAGES[language].exes]
        found_exes = [
            exe for exe in candidate_exes
            if any(resolve_compiler_path(args, language, f"{exe}{v}") for v in VERSIONS)
        ]
        if not found_exes:
            if user_specified_languages:
                exe_str = candidate_exes[0] if len(candidate_exes) == 1 else f"any of {', '.join(candidate_exes)}"
                print(f"Warning: Ignoring unsupported language {language} ({exe_str} binary not found in PATH)")
            continue

        if user_specified_languages and exes:
            missing_exes = [exe for exe in exes if exe not in found_exes]
            for m in missing_exes:
                print(f"Warning: Compiler binary '{m}' for language {language} not found in PATH")

        actual_exes = found_exes if exes else []
        if language in args.language_exes:
            args.language_exes[language] += actual_exes
        else:
            args.language_exes[language] = actual_exes

    if not args.language_exes and not user_specified_languages:
        args.language_exes = {name: list(spec.exes) for name, spec in LANGUAGES.items()}

    raw_ops = [x.strip().lower() for x in args.operations.split(",") if x.strip()]
    filtered_operations: list[Op] = []
    for op_str in raw_ops:
        try:
            filtered_operations.append(Op(op_str))
        except ValueError:
            print("Warning: Ignoring unsupported operation " + op_str)
    if args.ast_check and Op.AST_CHECK not in filtered_operations:
        filtered_operations.insert(0, Op.AST_CHECK)

    args.operations = filtered_operations

    results = {}

    if args.print_code:
        print(markdown_header('Generated Code:', 1))
        for lang_name, spec in LANGUAGES.items():
            if lang_name not in args.language_exes:
                continue
            task_args = copy.deepcopy(args)
            spec.limit_args(task_args)
            for templated in spec.templated_variants:
                tmpl_desc = " (templated)" if templated else ""
                print(markdown_header(f"{spec.name}{tmpl_desc}", 2))
                print(f"```{spec.extension}")
                code = generate_test_program_source(spec, task_args, templated,
                                                    order_sections=spec.order_sections)
                print(code.strip('\n'))
                print("```\n")

    print(markdown_header('Benchmark:', 1))

    tasks = []
    reported_warnings = set()
    for op in args.operations:
        for spec in LANGUAGES.values():
            if spec.name not in args.language_exes or op not in spec.ops:
                continue

            # Per-language scaling/stability limits live in the language's own block.
            task_args = copy.deepcopy(args)
            for warning in spec.limit_args(task_args):
                if warning not in reported_warnings:
                    reported_warnings.add(warning)
                    print(warning)

            for templated in spec.templated_variants:
                for r_idx in range(len(spec.runners)):
                    tasks.append((spec.name, r_idx, op, templated, copy.deepcopy(task_args)))

    op_weights = {Op.BUILD: 3, Op.COMPILE: 2, Op.CHECK: 1, Op.AST_CHECK: 0}

    def _task_weight(t):
        t_lang, _, t_op, t_tmpl, _ = t
        tier = LANGUAGES[t_lang].tier
        op_w = op_weights.get(t_op, 1)
        return (tier, 2 if t_tmpl else 1, op_w)

    tasks.sort(key=_task_weight, reverse=True)

    cpus, is_hetero = get_available_cpus()
    cpu_use_count = len(cpus) if is_hetero else max(1, len(cpus) - HOMOGENEOUS_CPU_RESERVE)
    core_desc = "performance CPU core(s)" if is_hetero else "CPU core(s)"
    print(f"Running benchmarks in parallel across {cpu_use_count} {core_desc} (1 worker per core)...")

    manager = mp.Manager()
    idx_counter = manager.Value('i', 0)
    lock = manager.Lock()
    print_lock = manager.Lock()
    active_tasks = manager.dict()
    status_line_len = manager.Value('i', 0)
    completed_counter = manager.Value('i', 0)

    global ROOT_PATH
    ROOT_PATH = tempfile.mkdtemp(prefix=TEMP_DIR_PREFIX, dir=TEMP_DIR_BASE)
    call_proc_dirs = {os.path.abspath(os.path.join(ROOT_PATH, f"proc_{MAIN_PID}"))}

    def cleanup_call_empty_dirs():
        if os.getpid() != MAIN_PID:
            return
        for proc_dir in sorted(call_proc_dirs, key=len, reverse=True):
            if os.path.isdir(proc_dir):
                for dirpath, _, _ in os.walk(proc_dir, topdown=False):
                    try:
                        os.rmdir(dirpath)
                    except OSError:
                        pass
        if ROOT_PATH and os.path.isdir(ROOT_PATH):
            for dirpath, _, _ in os.walk(ROOT_PATH, topdown=False):
                try:
                    os.rmdir(dirpath)
                except OSError:
                    pass
            try:
                os.rmdir(ROOT_PATH)
            except OSError:
                pass

    atexit.register(cleanup_call_empty_dirs)

    stream = sys.stderr if sys.stderr.isatty() else (sys.stdout if sys.stdout.isatty() else None)
    progress_mode = args.progress
    if progress_mode == "auto":
        if _supports_tree_progress(stream):
            progress_mode = "tree"
        elif stream is not None and stream.isatty():
            progress_mode = "line"
        else:
            progress_mode = "none"
    is_tree = (progress_mode == "tree")

    builtins.print = _make_locked_print(builtins.print, print_lock, status_line_len, is_tree)

    stop_monitor = threading.Event()
    monitor_thread = threading.Thread(
        target=_progress_monitor,
        args=(active_tasks, completed_counter, len(tasks), stop_monitor, print_lock,
              status_line_len, progress_mode),
        daemon=True,
    )
    monitor_thread.start()

    try:
        with mp.Pool(processes=cpu_use_count, initializer=_worker_init,
                     initargs=(cpus, idx_counter, lock, print_lock, active_tasks,
                               status_line_len, ROOT_PATH, is_tree)) as pool:
            for p in getattr(pool, '_pool', []):
                if getattr(p, 'pid', None):
                    call_proc_dirs.add(os.path.abspath(os.path.join(ROOT_PATH, f"proc_{p.pid}")))
            for res, worker_pid in pool.imap_unordered(_run_task, tasks):
                completed_counter.value += 1
                call_proc_dirs.add(os.path.abspath(os.path.join(ROOT_PATH, f"proc_{worker_pid}")))
                if res:
                    _merge_results(results, res)
    except KeyboardInterrupt:
        print("\nBenchmark interrupted by user.", file=sys.stderr)
        sys.exit(130)
    finally:
        stop_monitor.set()
        monitor_thread.join(timeout=MONITOR_JOIN_TIMEOUT_SEC)
        with print_lock:
            if status_line_len.value > 0:
                stream = sys.stderr if sys.stderr.isatty() else (sys.stdout if sys.stdout.isatty() else None)
                if stream is not None:
                    _clear_status(stream, status_line_len.value, is_tree)
                status_line_len.value = 0
        cleanup_call_empty_dirs()

    print()
    print(markdown_table(table_titles(args.values, results), results, values_mode=args.values,
                          highlight=args.highlight_min, sort_by=args.sort, sort_reverse=args.sort_reverse))


if __name__ == '__main__':
    main()
