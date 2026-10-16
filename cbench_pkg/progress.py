"""
Live progress display for the parallel benchmark runner.

Renders either a compact single line or a tree view of currently active
benchmark tasks on the terminal while the pool runs.
"""

import os
import re
import sys
import time
import shutil


PROGRESS_POLL_INTERVAL_SEC = 0.2
MONITOR_JOIN_TIMEOUT_SEC = 1.0


def _format_duration(secs: float) -> str:
    if secs < 60:
        return f"{secs:.1f}s"
    m = int(secs // 60)
    s = int(secs % 60)
    return f"{m}m{s:02d}s"


def _supports_tree_progress(stream) -> bool:
    if stream is None or not getattr(stream, "isatty", lambda: False)():
        return False
    term = os.environ.get("TERM", "").lower()
    if term in ("dumb", "emacs"):
        return False
    inside_emacs = os.environ.get("INSIDE_EMACS", "").lower()
    if inside_emacs and "vterm" not in inside_emacs:
        return False
    if os.name != "nt" and not term:
        return False
    return True


def _clear_status(stream, count, is_tree=False):
    if count > 0:
        if is_tree:
            stream.write("\r\x1b[2K")
            for _ in range(count - 1):
                stream.write("\x1b[1A\r\x1b[2K")
        else:
            stream.write("\r" + (" " * count) + "\r")
        stream.flush()


def _parse_task_desc(desc):
    m = re.match(r"^(.*?)(?:\s+\(templated\))?(?:\s+\(([^)]+)\))?\s+\[([^\]]+)\]$", desc)
    if m:
        lang = m.group(1).strip()
        templated = "(templated)" in desc
        cexe = m.group(2)
        op = m.group(3)
        parts = [f"[{op}]"]
        if templated:
            parts.append("(templated)")
        if cexe:
            parts.append(f"({cexe})")
        return lang, " ".join(parts)
    return desc, ""


def _make_locked_print(orig_print, print_lock, status_len, is_tree=False):
    def _locked_print(*args, **kwargs):
        with print_lock:
            if status_len is not None and status_len.value > 0:
                stream = sys.stderr if sys.stderr.isatty() else (sys.stdout if sys.stdout.isatty() else None)
                if stream is not None:
                    _clear_status(stream, status_len.value, is_tree)
                status_len.value = 0
            orig_print(*args, **kwargs)
            dest = kwargs.get("file") or sys.stdout
            if hasattr(dest, "flush"):
                dest.flush()
    return _locked_print


def _progress_monitor(active_tasks, completed_counter, total_tasks, stop_event, print_lock,
                      status_len, progress_mode="tree"):
    stream = sys.stderr if sys.stderr.isatty() else (sys.stdout if sys.stdout.isatty() else None)
    if stream is None or progress_mode == "none":
        return

    while not stop_event.wait(PROGRESS_POLL_INTERVAL_SEC):
        try:
            current_tasks = list(active_tasks.values())
        except Exception:
            continue

        now = time.time()
        current_tasks.sort(key=lambda item: item[1])

        done = completed_counter.value
        term_size = shutil.get_terminal_size((80, 24))
        term_cols = term_size.columns
        term_lines = term_size.lines

        if progress_mode == "line":
            items_parts = []
            for desc, start_t in current_tasks:
                dur_str = _format_duration(max(0.0, now - start_t))
                items_parts.append(f"{desc} {dur_str}")

            header = f"[{done}/{total_tasks}] Active: "
            if not items_parts:
                status_text = f"[{done}/{total_tasks}] Waiting for tasks..."
            else:
                avail = max(10, term_cols - len(header) - 1)
                line = ""
                for idx, part in enumerate(items_parts):
                    candidate = (line + ", " + part) if line else part
                    rem_count = len(items_parts) - (idx + 1)
                    rem_suffix = f" (+{rem_count} more)" if rem_count > 0 else ""
                    if len(candidate) + len(rem_suffix) <= avail:
                        line = candidate
                    else:
                        if not line:
                            line = candidate[:avail]
                        elif rem_count > 0:
                            line += rem_suffix
                        break
                status_text = header + line

            with print_lock:
                pad = max(0, status_len.value - len(status_text))
                stream.write("\r" + status_text + (" " * pad) + "\r" + status_text)
                stream.flush()
                status_len.value = len(status_text) + pad
        else:
            if not current_tasks:
                tree_lines = [f"[{done}/{total_tasks}] Waiting for tasks..."]
            else:
                max_tasks = max(4, min(10, term_lines - 6))
                visible_tasks = current_tasks[:max_tasks]
                rem_count = len(current_tasks) - len(visible_tasks)

                grouped = {}
                for desc, start_t in visible_tasks:
                    lang, sub_desc = _parse_task_desc(desc)
                    dur_str = _format_duration(max(0.0, now - start_t))
                    grouped.setdefault(lang, []).append((sub_desc, dur_str))

                max_sub_len = max((len(sub) for items in grouped.values() for sub, _ in items), default=0)

                tree_lines = [f"[{done}/{total_tasks}] Active:"]
                has_more = rem_count > 0
                lang_list = list(grouped.items())
                for l_idx, (lang, items) in enumerate(lang_list):
                    is_last_lang = (l_idx == len(lang_list) - 1) and not has_more
                    lang_branch = "└── " if is_last_lang else "├── "
                    tree_lines.append(f"{lang_branch}{lang}")
                    child_indent = "    " if is_last_lang else "│   "
                    for i_idx, (sub_desc, dur_str) in enumerate(items):
                        is_last_item = (i_idx == len(items) - 1)
                        item_branch = "└── " if is_last_item else "├── "
                        if sub_desc:
                            tree_lines.append(f"{child_indent}{item_branch}{sub_desc:<{max_sub_len}}  {dur_str}")
                        else:
                            tree_lines.append(f"{child_indent}{item_branch}{dur_str}")

                if has_more:
                    tree_lines.append(f"└── (+{rem_count} more)")

            tree_lines = [line[:term_cols] for line in tree_lines]

            with print_lock:
                _clear_status(stream, status_len.value, is_tree=True)
                status_text = "\n".join(tree_lines)
                stream.write(status_text)
                stream.flush()
                status_len.value = len(tree_lines)
