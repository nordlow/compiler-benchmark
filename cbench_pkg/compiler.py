"""
Compiler execution engine.

Measures compilation duration, peak RSS, and exit codes for a single
compiler invocation, and drives the per-operation benchmark loop
(`benchmark_compiler_op`) that the language runners call into.
"""

import os
import os.path
import stat
import subprocess as sp
import sys
import time
import builtins
import copy
import tempfile
import shutil
import atexit
import glob
from functools import cache
from timeit import default_timer as timer

import psutil

from .types import (
    Lang,
    Exec,
    LangSupport,
    ResultKey,
    RawCol,
    DUR_COLS,
    lang_support,
    DEFAULT_TIMEOUT,
    ADAPTIVE_FAST_DUR_THRESHOLD,
    ADAPTIVE_FAST_RUN_COUNT,
    ADAPTIVE_SLOW_DUR_THRESHOLD,
    ADAPTIVE_SLOW_RUN_COUNT,
)
from .reporting import sourceIdOf, is_machine_code_binary
from .version import resolve_compiler_path, find_compiler_versions, get_compiler_version
from .generation import generate_test_program_file
from .timer import ProcessTimer
from .progress import _make_locked_print


DEFAULT_RUN_TIMEOUT = 10.0

# These are set by `main()` in cli.py.
ROOT_PATH = None
MAIN_PID = None
_worker_active_tasks = None
_worker_status_len = None


def out_directory(lang: str) -> str:
    return os.path.abspath(os.path.join(ROOT_PATH, f"proc_{os.getpid()}", lang.lower()))


def out_binary(lang: str) -> str:
    return lang_support(lang).out_binary


@cache
def get_gcc_lib_dir() -> str | None:
    from shutil import which
    for cc in ('gcc', 'cc', 'clang'):
        cc_path = which(cc)
        if cc_path:
            try:
                res = sp.run([cc_path, '-print-file-name=crtbegin.o'], stdout=sp.PIPE, stderr=sp.DEVNULL, text=True)
                out = res.stdout.strip()
                if out and out != 'crtbegin.o' and os.path.isfile(out):
                    return os.path.dirname(out)
            except Exception:
                pass
    matches = sorted(glob.glob('/usr/lib/gcc/*/*/crtbegin.o'))
    if matches:
        return os.path.dirname(matches[-1])
    return None


C_WARN_FLAGS = ['-Wall', '-Wextra']
CXX_WARN_FLAGS = ['-Wno-c++11-extensions']


def gcc_clang_op_flags(op, lang):
    if op == 'check':
        cexe_flags = ['-fsyntax-only']
        out_flag_and_exe = []
    elif op == 'compile':
        cexe_flags = ['-c']
        out_flag_and_exe = []
    elif op == 'build':
        cexe_flags = []
        out_flag_and_exe = ['-o', out_binary(lang)]
    else:
        return (None, None)
    return (cexe_flags, out_flag_and_exe)


def bm_C_and_Cxx_using_gcc(results: Results, lang, code_paths, args: argparse.Namespace, op, templated: bool):
    (cexe_flags, out_flag_and_exe) = gcc_clang_op_flags(op, lang)
    if cexe_flags is None:
        return None
    flags = (C_WARN_FLAGS if lang == 'C' else CXX_WARN_FLAGS) + cexe_flags
    base = 'gcc' if lang == 'C' else 'g++'
    for cexe in find_compiler_versions(args, lang, base):
        benchmark_compiler_op(code_paths, out_flag_and_exe, cexe, True, flags, args, op,
                              get_compiler_version(cexe), lang, templated, results)


def bm_C_and_Cxx_using_clang(results: Results, lang, code_paths, args: argparse.Namespace, op, templated: bool):
    (cexe_flags, out_flag_and_exe) = gcc_clang_op_flags(op, lang)
    if cexe_flags is None:
        return None
    warn = (C_WARN_FLAGS + ['-fno-color-diagnostics', '-fno-caret-diagnostics', '-fno-diagnostics-show-option']) if lang == 'C' else CXX_WARN_FLAGS
    base = 'clang' if lang == 'C' else 'clang++'
    for cexe in find_compiler_versions(args, lang, base):
        benchmark_compiler_op(code_paths, out_flag_and_exe, cexe, True, warn + cexe_flags, args, op,
                              get_compiler_version(cexe), lang, templated, results)


def build_compiler_cmd(lang: str, cexe: str, cexe_flags: list, out_flags: list, src_name: str,
                       has_stdin: bool) -> list:
    """Construct the argv; a language may override the ordering via LangSupport.build_cmd."""
    if has_stdin:
        return [cexe] + cexe_flags + out_flags
    hook = lang_support(lang).build_cmd
    if hook is not None:
        return hook(cexe, cexe_flags, out_flags, src_name)
    return [cexe] + cexe_flags + out_flags + [src_name]


def measure_compilation(p_args: list, work_dir: str, sample_rate: int,
                        stdin_text: str | None = None,
                        timeout: float | None = DEFAULT_TIMEOUT):
    """Execute compiler in work_dir and measure duration, RSS, and exit code."""
    cwd = os.getcwd()
    os.chdir(work_dir)
    cstart = timer()
    outs, errs = b'', b''
    returncode = -1
    rss_mu = None

    try:
        if stdin_text is not None:
            comp_proc = sp.Popen(p_args, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
            comp_proc.stdin.write(stdin_text.encode('utf-8'))
            comp_proc.stdin.close()
            try:
                p = psutil.Process(comp_proc.pid)
                max_rss = 0
                while comp_proc.poll() is None:
                    if timeout and (timer() - cstart) > timeout:
                        comp_proc.kill()
                        returncode = 124
                        errs = b'Process timed out'
                        break
                    try:
                        rss = p.memory_info().rss
                        if rss > max_rss:
                            max_rss = rss
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        break
                    time.sleep(1.0 / sample_rate)
                rss_mu = max_rss if max_rss > 0 else "missing"
            except Exception:
                rss_mu = "sampling error"
            outs, errs = comp_proc.communicate()
            returncode = comp_proc.returncode
        else:
            pt = ProcessTimer(args=p_args)
            try:
                while pt.poll():
                    if timeout and (timer() - cstart) > timeout:
                        try:
                            pt.comp_proc.kill()
                        except Exception:
                            pass
                        returncode = 124
                        errs = b'Process timed out'
                        break
                    time.sleep(1.0 / sample_rate)
            except Exception:
                rss_mu = "sampling error"
            finally:
                if rss_mu is None and getattr(pt, 'max_rss_mu', 0) != 0:
                    rss_mu = pt.max_rss_mu
                rss_mu = rss_mu or "missing"

            outs, errs = pt.comp_proc.communicate()
            returncode = pt.comp_proc.returncode
    finally:
        os.chdir(cwd)

    dur = timer() - cstart
    return dur, returncode, outs, errs, rss_mu


def run_compiled_file(args: list, run_count=1, timeout=DEFAULT_RUN_TIMEOUT):
    durs = []
    for _ in range(0, run_count):
        cstart = timer()
        try:
            sp.run(args, stdout=sp.DEVNULL, stderr=sp.DEVNULL, timeout=timeout)
            durs.append(timer() - cstart)
        except sp.TimeoutExpired:
            return None
    return min(durs) if durs else None


def run_target_binary(cexe: str, lang: str, lang_dir: str, exec_cmd, op: str,
                      src_name: str, run_count: int):
    """Execute target binary or script, handling compiler-specific quirks."""
    if op == 'build' and exec_cmd:
        outb_path = os.path.join(lang_dir, out_binary(lang))
        if exec_cmd is True:
            if os.path.exists(outb_path) and not os.access(outb_path, os.X_OK):
                os.chmod(outb_path, os.stat(outb_path).st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
            return run_compiled_file(outb_path, run_count=run_count, timeout=DEFAULT_RUN_TIMEOUT)
        if isinstance(exec_cmd, list):
            return run_compiled_file(exec_cmd + [outb_path], run_count=run_count, timeout=DEFAULT_RUN_TIMEOUT)

    return None


def benchmark_compiler_op(code_paths: dict,
                          out_flag_and_exe: list,
                          cexe: str,
                          exec_cmd,
                          cexe_flags: list[str],
                          args,
                          op: str,
                          compiler_version: str | None = None,
                          lang: str = None,
                          templated: bool = False,
                          results: dict = {},
                          stdin_input: str | None = None):
    spec = lang_support(lang)
    key = ResultKey(Lang(lang), templated, Exec(cexe))
    row = results.setdefault(key, {})
    row[RawCol.LANG] = lang
    row[RawCol.TEMPLATED] = 'Yes' if templated else 'No'
    row[RawCol.CEXE_VERSION] = compiler_version
    row[RawCol.CEXE_PATH] = os.path.basename(cexe)
    lang_dir = os.path.abspath(out_directory(lang))
    total_funcs = args.function_count * args.function_depth

    durs = []
    rss_mu = None
    worker_pid = os.getpid()
    tmpl_suffix = " (templated)" if templated else ""
    cname = os.path.basename(cexe)
    if _worker_active_tasks is not None:
        _worker_active_tasks[worker_pid] = (f"{lang}{tmpl_suffix} ({cname}) [{op}]", time.time())

    for run_ix in range(args.run_count):
        src_key = sourceIdOf(lang, templated, run_ix)
        if src_key in code_paths:
            src_path = code_paths[src_key]
        else:
            src_path = generate_test_program_file(lang, args, templated, run_ix,
                                                  program_dir=spec.program_dir,
                                                  source_filename=spec.source_filename,
                                                  order_sections=spec.order_sections)
            code_paths[src_key] = src_path
        src_name = os.path.relpath(src_path, lang_dir)

        p_args = build_compiler_cmd(lang, cexe, cexe_flags, out_flag_and_exe, src_name,
                                    has_stdin=bool(stdin_input))
        stdin_text = stdin_input.format(run_ix) if stdin_input else None

        timeout_sec = getattr(args, 'timeout', DEFAULT_TIMEOUT)
        dur, returncode, outs, errs, rss = measure_compilation(p_args, lang_dir, args.sample_rate,
                                                               stdin_text, timeout=timeout_sec)
        rss_mu = rss

        out_str = outs.decode('utf8', errors='ignore') if outs else ''
        err_str = errs.decode('utf8', errors='ignore') if errs else ''
        if lang == 'Scala':
            err_str = '\n'.join([
                line for line in err_str.splitlines()
                if 'sun.misc.Unsafe' not in line and 'scala.runtime.LazyVals$' not in line and 'Please consider reporting this' not in line
            ]).strip()
        has_out = bool(out_str.strip())
        has_err = bool(err_str.strip())
        if has_err or has_out or returncode != 0:
            setattr(args, 'has_stderr', True)
            setattr(args, 'has_output', True)
        if returncode != 0:
            setattr(args, 'has_stderr', True)
            setattr(args, 'has_output', True)
            cmd_str = ' '.join(p_args)
            if returncode in (-9, 124):
                t_limit = getattr(args, 'timeout', 60.0)
                timeout_tag = f">{int(t_limit) if t_limit.is_integer() else t_limit:.1f}s"
                print(f"WARNING: Compilation `{cmd_str}` timed out after {t_limit:.1f}s", file=sys.stderr)
                op_col = {
                    'ast-check': RawCol.AST_CHECK_DUR,
                    'check': RawCol.CHECK_DUR,
                    'compile': RawCol.COMPILE_DUR,
                    'build': RawCol.BUILD_DUR,
                    'run': RawCol.RUN_DUR,
                }.get(op)
                if op_col is not None:
                    row[op_col] = timeout_tag
            else:
                print(f"WARNING: Compilation `{cmd_str}` of source file `{src_name}` exited with return code {returncode}", file=sys.stderr)
            if has_out:
                print(f"  - stdout: {out_str.strip()}", file=sys.stderr)
            if has_err:
                print(f"  - stderr: {err_str.strip()}", file=sys.stderr)
            if rss_mu and isinstance(rss_mu, (int, float)):
                slot = RawCol.CHECK_RSS if op == 'check' else (RawCol.BUILD_RSS if op == 'build' else None)
                if slot:
                    row[slot] = rss_mu / total_funcs
            return None
        else:
            if has_err:
                print(f"  - stderr: {err_str.strip()}", file=sys.stderr)

        durs.append(dur)
        if dur >= ADAPTIVE_SLOW_DUR_THRESHOLD and len(durs) >= ADAPTIVE_SLOW_RUN_COUNT:
            break
        elif dur >= ADAPTIVE_FAST_DUR_THRESHOLD and len(durs) >= ADAPTIVE_FAST_RUN_COUNT:
            break

    dur_min = min(durs)
    if _worker_active_tasks is not None:
        _worker_active_tasks[worker_pid] = (f"{lang}{tmpl_suffix} ({cname}) [run]", time.time())
    run_dur_min = run_target_binary(cexe, lang, lang_dir, exec_cmd, op, src_name, args.run_count)
    if _worker_active_tasks is not None:
        _worker_active_tasks[worker_pid] = (f"{lang}{tmpl_suffix} ({cname}) [{op}]", time.time())

    output_size = None
    if op == 'build':
        outb_path = os.path.join(lang_dir, out_binary(lang))
        if is_machine_code_binary(outb_path, lang, cexe):
            try:
                output_size = os.path.getsize(outb_path)
            except OSError:
                output_size = None

    version_str = f' version {compiler_version}' if compiler_version is not None else ''
    cop = op.capitalize()
    if getattr(args, 'verbose', False):
        print(f'- {cop} took {dur_min:1.3f} seconds (using "{cexe}"{version_str})')

    row[RawCol.LANG] = lang
    row[RawCol.TEMPLATED] = 'Yes' if templated else 'No'
    row[RawCol.CEXE_VERSION] = compiler_version
    row[RawCol.CEXE_PATH] = os.path.basename(cexe)

    op_dur_col = {
        'ast-check': RawCol.AST_CHECK_DUR,
        'check': RawCol.CHECK_DUR,
        'compile': RawCol.COMPILE_DUR,
        'build': RawCol.BUILD_DUR,
        'run': RawCol.RUN_DUR,
    }.get(op)
    if op_dur_col is not None:
        row[op_dur_col] = dur_min / total_funcs

    if run_dur_min is not None:
        row[RawCol.RUN_DUR] = run_dur_min / total_funcs

    op_rss_col = {'check': RawCol.CHECK_RSS, 'build': RawCol.BUILD_RSS}.get(op)
    if op_rss_col is not None and rss_mu is not None:
        row[op_rss_col] = (rss_mu / total_funcs) if isinstance(rss_mu, (int, float)) else rss_mu

    if output_size is not None:
        row[RawCol.OUTPUT_SIZE] = output_size / total_funcs

    return row


def _worker_init(cpu_list, idx_counter, lock, print_lock, active_tasks, status_len, root_path,
                 is_tree=False):
    global _worker_active_tasks, _worker_status_len, ROOT_PATH, MAIN_PID
    _worker_active_tasks = active_tasks
    _worker_status_len = status_len
    ROOT_PATH = root_path
    MAIN_PID = os.getpid()
    with lock:
        idx = idx_counter.value
        idx_counter.value += 1
    cpu_id = cpu_list[idx % len(cpu_list)]
    if hasattr(os, 'sched_setaffinity'):
        try:
            os.sched_setaffinity(0, {cpu_id})
        except Exception:
            pass
    builtins.print = _make_locked_print(builtins.print, print_lock, status_len, is_tree)


def _run_task(task):
    from .types import LANGUAGES, Lang, Exec
    lang, r_idx, op, templated, task_args = task
    runner = LANGUAGES[lang].runners[r_idx]
    task_results, task_code_paths = {}, {}
    success = False
    task_args.has_stderr = False
    task_args.has_output = False
    lang_dir = out_directory(lang)
    proc_dir = os.path.dirname(lang_dir)
    worker_pid = os.getpid()
    tmpl_suffix = " (templated)" if templated else ""
    if _worker_active_tasks is not None:
        _worker_active_tasks[worker_pid] = (f"{lang}{tmpl_suffix} [{op}]", time.time())
    try:
        runner(task_results, task_code_paths, task_args, op, templated)
        if not getattr(task_args, 'has_stderr', False) and not getattr(task_args, 'has_output', False):
            success = True
    finally:
        if _worker_active_tasks is not None:
            _worker_active_tasks.pop(worker_pid, None)
        if success:
            shutil.rmtree(lang_dir, ignore_errors=True)
            try:
                os.rmdir(proc_dir)
            except OSError:
                pass
    return task_results, os.getpid()


def _merge_results(target, incoming):
    for key, row in incoming.items():
        if key not in target:
            target[key] = dict(row)
        else:
            for k, val in row.items():
                if val is not None:
                    target[key][k] = val
