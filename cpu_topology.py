"""
CPU topology and heterogeneous performance-core detection.
"""

import os
import sys
import shutil
import subprocess as sp
from collections.abc import Callable
import psutil


def _parse_cpulist(text: str) -> set[int]:
    """Parse standard kernel CPU list notation (e.g. '0-3,6,8-11')."""
    cores = set()
    for part in text.strip().split(","):
        if not part:
            continue
        if "-" in part:
            lo, hi = map(int, part.split("-", 1))
            cores.update(range(lo, hi + 1))
        else:
            cores.add(int(part))
    return cores


def _filter_primary_smt_threads(cpu_ids: list[int]) -> list[int]:
    """Pick only one logical thread per physical core to avoid SMT contention."""
    seen_physical_cores = set()
    primary_threads = []
    for c in cpu_ids:
        core_id_path = f"/sys/devices/system/cpu/cpu{c}/topology/core_id"
        if os.path.isfile(core_id_path):
            try:
                core_id = int(open(core_id_path).read().strip())
                if core_id not in seen_physical_cores:
                    seen_physical_cores.add(core_id)
                    primary_threads.append(c)
                continue
            except (OSError, ValueError):
                pass
        # Fallback if topology/core_id is missing: take thread as is
        primary_threads.append(c)
    return primary_threads if primary_threads else cpu_ids


def _detect_intel_hybrid(available: list[int]) -> list[int] | None:
    """Linux Intel Hybrid (Alder Lake / Raptor Lake) PMU & core_type topology."""
    # Strategy 1: Linux 5.18+ sysfs core_type (0x20 = P-core, 0x40 = E-core)
    p_threads = []
    has_core_type = False
    for c in available:
        type_file = f"/sys/devices/system/cpu/cpu{c}/topology/core_type"
        if os.path.isfile(type_file):
            try:
                has_core_type = True
                ctype = int(open(type_file).read().strip(), 0)
                # Intel: 0x40 is Atom (E-core), 0x20 is Core (P-core)
                if ctype != 0x40:
                    p_threads.append(c)
            except (OSError, ValueError):
                pass
    if has_core_type and 0 < len(p_threads) < len(available):
        return _filter_primary_smt_threads(p_threads)

    # Strategy 2: PMU cpumask
    for path in ("/sys/devices/cpu_core/cpus", "/sys/bus/event_source/devices/cpu_core/cpus"):
        if os.path.isfile(path):
            try:
                p_cores = _parse_cpulist(open(path).read())
                matching = [c for c in available if c in p_cores]
                if 0 < len(matching) < len(available):
                    return _filter_primary_smt_threads(matching)
            except OSError:
                pass
    return None


def _detect_cpu_capacity(available: list[int]) -> list[int] | None:
    """Linux ARM big.LITTLE / DynamIQ scheduler capacity."""
    caps = {}
    for c in available:
        cap_file = f"/sys/devices/system/cpu/cpu{c}/cpu_capacity"
        if os.path.isfile(cap_file):
            try:
                caps[c] = int(open(cap_file).read().strip())
            except (OSError, ValueError):
                pass
    if len(caps) == len(available) and len(set(caps.values())) > 1:
        max_cap = max(caps.values())
        matching = [c for c in available if caps[c] == max_cap]
        return _filter_primary_smt_threads(matching)
    return None


def _detect_frequency_heterogeneity(available: list[int]) -> list[int] | None:
    """High-level frequency inspection via psutil (Linux, FreeBSD)."""
    try:
        freqs = psutil.cpu_freq(percpu=True)
        if freqs and len(freqs) >= max(available) + 1:
            core_maxes = {c: freqs[c].max for c in available if freqs[c].max > 0}
            if len(core_maxes) == len(available) and len(set(core_maxes.values())) > 1:
                top_freq = max(core_maxes.values())
                return [c for c in available if core_maxes[c] == top_freq]
    except Exception:
        pass
    return None


def _detect_macos_perflevel(available: list[int]) -> list[int] | None:
    """macOS Apple Silicon (M-series) performance level sysctl."""
    if sys.platform != "darwin" or not shutil.which("sysctl"):
        return None
    try:
        nlevels = int(sp.check_output(["sysctl", "-n", "hw.nperflevels"], text=True).strip())
        if nlevels > 1:
            p_count = int(sp.check_output(["sysctl", "-n", "hw.perflevel0.logicalcpu"], text=True).strip())
            if 0 < p_count < len(available):
                return available[:p_count]
    except Exception:
        pass
    return None


# Ordered priority pipeline:
# PMU topology (most accurate) -> scheduler capacity -> per-core max freq -> macOS sysctl
CORE_DETECTION_STRATEGIES: list[Callable[[list[int]], list[int] | None]] = [
    _detect_intel_hybrid,
    _detect_cpu_capacity,
    _detect_frequency_heterogeneity,
    _detect_macos_perflevel,
]


def get_available_cpus() -> tuple[list[int], bool]:
    """Return available CPU IDs and whether heterogeneous performance cores were selected."""
    # High-level cross-platform affinity via psutil (respects taskset, sched_affinity, cgroups)
    try:
        cpus = sorted(psutil.Process().cpu_affinity())
    except (AttributeError, psutil.Error):
        cpus = list(range(psutil.cpu_count(logical=True) or 1))

    for strategy in CORE_DETECTION_STRATEGIES:
        p_cpus = strategy(cpus)
        if p_cpus:
            return p_cpus, True

    return cpus, False
