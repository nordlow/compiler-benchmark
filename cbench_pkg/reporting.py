"""
Result rendering and Markdown tables.

Formats raw benchmark durations/RSS/sizes into the per-column display strings,
merges plain + templated variants into stacked cells, and renders the three
tier tables (minimalist / AOT systems / managed & VM).
"""

import os
from prettytable import PrettyTable, TableStyle

from .types import LangSupport, lang_support, Op, RawCol, DUR_COLS, Results


FIELD_WIDTH = 6

# Precomputed once when the module loads
FMT_1F = f"%{FIELD_WIDTH}.1f"
FMT_0F = f"%{FIELD_WIDTH}.0f"


class Column:
    def __init__(self, name: str, unit: str | None = None):
        self.name = name
        self.unit = unit

    def header(self, values_mode: str = 'absolute') -> str:
        if not self.unit:
            return self.name
        if values_mode == 'relative':
            return f"{self.name} [x]"
        return f"{self.name} [{self.unit}]"


TABLE_COLUMNS = [
    Column('Language (Exec)'),
    Column('Total=Build+Run', 'µs/f'),
    Column('Check', 'µs/f'),
    Column('Compile', 'µs/f'),
    Column('Check RSS', 'kB/f'),
    Column('Build RSS', 'kB/f'),
    Column('Output Size', 'B/f'),
]


def table_titles(values_mode: str = "absolute", results: Results | None = None) -> list[str]:
    if not results:
        return [col.header(values_mode) for col in TABLE_COLUMNS]
    time_units = get_column_time_units(results)
    check_u = time_units.get(RawCol.CHECK_DUR, ("µs/f", 1e6))[0]
    compile_u = time_units.get(RawCol.COMPILE_DUR, ("µs/f", 1e6))[0]

    cols = [
        Column("Language (Exec)"),
        Column("Total=Build+Run", "µs/f"),
        Column("Check", check_u),
        Column("Compile", compile_u),
        Column("Check RSS", "kB/f"),
        Column("Build RSS", "kB/f"),
        Column("Output Size", "B/f"),
    ]
    return [col.header(values_mode) for col in cols]


MARKDOWN_TABLE_TITLES = table_titles('absolute')


def is_machine_code_binary(path: str, lang: str, cexe: str) -> bool:
    if not os.path.isfile(path):
        return False
    if not lang_support(lang).native_output(cexe):
        return False
    try:
        with open(path, 'rb') as f:
            magic = f.read(4)
            macho_magics = {
                bytes([0xfe, 0xed, 0xfa, 0xce]),
                bytes([0xfe, 0xed, 0xfa, 0xcf]),
                bytes([0xce, 0xfa, 0xed, 0xfe]),
                bytes([0xcf, 0xfa, 0xed, 0xfe]),
                bytes([0xca, 0xfe, 0xba, 0xbe]),
            }
            return (
                magic.startswith(bytes([0x7f, 0x45, 0x4c, 0x46])) or
                magic in macho_magics or
                magic.startswith(b"MZ")
            )
    except OSError:
        return False


def sourceIdOf(lang: str, templated: bool, run_ix):
    return f"{lang}-{'Templated' if templated else 'Untemplated'}-{run_ix}"


def format_metric_columns(results: Results, col: RawCol, values_mode: str = "absolute",
                          highlight: bool = False, time_unit: tuple[str, float] | None = None):
    min_vals = {False: None, True: None}
    for key, result in results.items():
        templated = key[1]
        val = result.get(col)
        if isinstance(val, (int, float)):
            if min_vals[templated] is None or (min_vals[templated] > val):
                min_vals[templated] = val

    for key, result in results.items():
        templated = key[1]
        result[col] = stringify_metrics(abs_n=result.get(col),
                                        min_val=min_vals[templated],
                                        col=col,
                                        values_mode=values_mode,
                                        highlight=highlight,
                                        time_unit=time_unit)


def stringify_metrics(abs_n, min_val, col: RawCol, values_mode: str = "absolute",
                      highlight: bool = False,
                      time_unit: tuple[str, float] | None = None):
    if isinstance(abs_n, str):
        return "{:>13}".format(abs_n)
    if abs_n is None:
        return "{:>6}".format("N/A")

    if col in DUR_COLS:
        if time_unit is not None:
            u_str, _ = time_unit
            if u_str.startswith("ns"):
                abs_str = to_str_in_nanoseconds(abs_n)
            elif u_str.startswith("ms"):
                abs_str = to_str_in_milliseconds(abs_n)
            elif u_str.startswith("s"):
                abs_str = to_str_in_seconds(abs_n)
            else:
                abs_str = to_str_in_microseconds(abs_n)
        elif col == RawCol.RUN_DUR:
            abs_str = to_str_in_nanoseconds(abs_n)
        else:
            abs_str = to_str_in_microseconds(abs_n)
    elif col in (RawCol.CHECK_RSS, RawCol.BUILD_RSS):
        abs_str = to_str_memory_usage(abs_n)
    elif col == RawCol.OUTPUT_SIZE:
        abs_str = to_str_output_size(abs_n)
    else:
        abs_str = str(abs_n)

    is_min = min_val is not None and abs_n == min_val
    abs_str = abs_str.strip()

    def _hl(text: str) -> str:
        return (
            f'<span style="color:#0a7f2e;background-color:#e6f7ec;font-weight:bold">{text}</span>'
            if highlight and is_min else text
        )

    if is_min:
        rel_str = " (1.0)"
        rel_only = "1.0"
    elif not min_val:
        rel_str = " (N/A)"
        rel_only = "N/A"
    else:
        rel_n = abs_n / min_val
        rel_str = " (" + factor_str(rel_n) + ")"
        rel_only = factor_str(rel_n)

    if values_mode == 'relative':
        return _hl(rel_only)
    elif values_mode == 'both':
        return _hl(abs_str) + rel_str
    else:
        return _hl(abs_str)


def to_str_in_seconds(dur):
    return FMT_1F % dur if dur is not None else ""


def to_str_in_milliseconds(dur):
    return FMT_1F % (1e3 * dur) if dur is not None else ""


def to_str_in_microseconds(dur):
    return FMT_1F % (1e6 * dur) if dur is not None else ""


def to_str_in_nanoseconds(dur):
    return FMT_0F % (1e9 * dur) if dur is not None else ""


def factor_str(factor):
    return f"{factor:.1f}"


def to_str_memory_usage(mu):
    return f"{mu / 1e3:{FIELD_WIDTH}.1f}"


def to_str_output_size(size):
    return f"{size:{FIELD_WIDTH}.1f}"


def markdown_header(text: str, nr: int):
    return '#' * nr + ' ' + text


def pick_time_unit_and_scale(values: list) -> tuple[str, float]:
    """Pick standard SI unit and scale (s/f, ms/f, µs/f, ns/f) keeping values in [1, 1000)."""
    valid = [v for v in values if isinstance(v, (int, float)) and v > 0]
    if not valid:
        return ("µs/f", 1e6)
    valid.sort()
    rep = valid[len(valid) // 2]
    if rep >= 1.0:
        return ("s/f", 1.0)
    elif rep >= 1e-3:
        return ("ms/f", 1e3)
    elif rep >= 1e-6:
        return ("µs/f", 1e6)
    else:
        return ("ns/f", 1e9)


def get_column_time_units(results: Results) -> dict[RawCol, tuple[str, float]]:
    # µs/f provides standard microsecond precision without rounding sub-ms compilers to 0.0
    return {col: ("µs/f", 1e6) for col in DUR_COLS}


def merge_plain_and_templated_results(results: Results, values_mode: str = "absolute",
                                      highlight: bool = False):
    metric_cols = [
        RawCol.CHECK_DUR,
        RawCol.COMPILE_DUR,
        RawCol.CHECK_RSS,
        RawCol.BUILD_RSS,
        RawCol.OUTPUT_SIZE,
    ]
    min_tots = {False: None, True: None}
    for (_, templated, _), row in results.items():
        b = row.get(RawCol.BUILD_DUR)
        r = row.get(RawCol.RUN_DUR)
        if b is not None or r is not None:
            tot = (b if isinstance(b, (int, float)) else 0.0) + (r if isinstance(r, (int, float)) else 0.0)
            if min_tots[templated] is None or tot < min_tots[templated]:
                min_tots[templated] = tot

    merged = {}
    grouped = {}
    for (lang, templated, cexec), row in results.items():
        grouped.setdefault((lang, cexec), {})[templated] = row

    for (lang, cexec), variants in grouped.items():
        row_plain = variants.get(False)
        row_tmpl = variants.get(True)
        base_row = row_plain if row_plain is not None else row_tmpl
        version = base_row.get(RawCol.CEXE_VERSION)
        version_str = f" {version}" if version and version != "unknown" else ""
        merged_row = [f"{base_row.get(RawCol.LANG)} ({base_row.get(RawCol.CEXE_PATH)}{version_str})"]
        has_ast_check = Op.AST_CHECK.value in lang_support(str(lang)).ops

        def format_tot(row, tmpl):
            if row is None:
                return None
            b = row.get(RawCol.BUILD_DUR)
            r = row.get(RawCol.RUN_DUR)
            if isinstance(b, str):
                return b
            if b is None and r is None:
                return None
            b_val = b if isinstance(b, (int, float)) else 0.0
            r_val = r if isinstance(r, (int, float)) else 0.0
            tot_val = b_val + r_val
            b_us, r_us, tot_us = b_val * 1e6, r_val * 1e6, tot_val * 1e6
            r_str = "0.0" if r_us == 0.0 else (f"{r_us:.2f}" if r_us < 1.0 else f"{r_us:.1f}")
            abs_str = f"{tot_us:.0f}={b_us:.0f}+{r_str}"
            m = min_tots[tmpl]
            is_min = m is not None and tot_val == m

            def _hl(txt):
                return f'<span style="color:#0a7f2e;background-color:#e6f7ec;font-weight:bold">{txt}</span>' if highlight and is_min else txt

            if is_min:
                rel_only, rel_str = "1.0", " (1.0)"
            else:
                rn = tot_val / m if m else 1.0
                rel_only, rel_str = factor_str(rn), f" ({factor_str(rn)})"
            if values_mode == "relative":
                return _hl(rel_only)
            elif values_mode == "both":
                return _hl(abs_str) + rel_str
            return _hl(abs_str)

        tot_p = format_tot(row_plain, False)
        tot_t = format_tot(row_tmpl, True)
        p_tot_na = (tot_p is None)
        t_tot_na = (tot_t is None)

        if p_tot_na and t_tot_na:
            tot_cell = "N/A"
        elif row_tmpl is None:
            tot_cell = tot_p if not p_tot_na else "N/A"
        elif p_tot_na:
            tot_cell = f"-<br>{tot_t}"
        elif t_tot_na:
            tot_cell = f"{tot_p}<br>-"
        else:
            tot_cell = f"{tot_p}<br>{tot_t}"

        merged_row.append(tot_cell)

        def format_col(col_key):
            val_p = str(row_plain[col_key]).strip() if row_plain and row_plain.get(col_key) is not None else None
            val_t = str(row_tmpl[col_key]).strip() if row_tmpl and row_tmpl.get(col_key) is not None else None

            p_na = (val_p is None or val_p == 'N/A')
            t_na = (val_t is None or val_t == 'N/A')

            if p_na and t_na:
                return 'N/A'
            elif row_tmpl is None:
                return val_p if not p_na else 'N/A'
            elif p_na:
                return f"-<br>{val_t}"
            elif t_na:
                return f"{val_p}<br>-"
            else:
                return f"{val_p}<br>{val_t}"

        for col in metric_cols:
            cell = format_col(col)
            if col == RawCol.CHECK_DUR and has_ast_check:
                ast_cell = format_col(RawCol.AST_CHECK_DUR)
                if ast_cell != 'N/A':
                    cell = f"{cell}<br>{ast_cell}"
            merged_row.append(cell)

        merged[(lang, cexec)] = merged_row

    return merged


TIERS = [
    (
        2,
        "Modern Systems Languages (Ahead-of-Time)",
        "Full type inference, monomorphization/generics, semantic safety, module systems.",
    ),
    (
        1,
        "Single-Pass / Minimalist Compilers",
        "No SSA optimization, no borrow checking, trivial type systems, instant code emission.",
    ),
    (
        3,
        "Managed & VM / JIT / Scripting",
        "Bytecode emission, runtime metadata, GC runtimes.",
    ),
]


def get_semantic_tier(lang: str, cexe: str) -> int:
    spec = lang_support(lang)
    base = os.path.basename(cexe).lower()
    for prefix, tier in spec.exe_tiers.items():
        if base.startswith(prefix):
            return tier
    return spec.tier


def _extract_metric(variants, col: RawCol):
    for row in (variants.get(False), variants.get(True)):
        if row is None:
            continue
        v = row.get(col)
        if isinstance(v, (int, float)):
            return float(v)
        if isinstance(v, str) and v.startswith(">"):
            return float("inf")
    return None


def _extract_total(variants):
    for row in (variants.get(False), variants.get(True)):
        if row is None:
            continue
        b, r = row.get(RawCol.BUILD_DUR), row.get(RawCol.RUN_DUR)
        if (isinstance(b, str) and b.startswith(">")) or (isinstance(r, str) and r.startswith(">")):
            return float("inf")
        if isinstance(b, (int, float)) or isinstance(r, (int, float)):
            return float((b if isinstance(b, (int, float)) else 0.0) + (r if isinstance(r, (int, float)) else 0.0))
    return None


def render_single_table(titles: list[str], results: Results, values_mode: str = "absolute",
                        highlight: bool = False, time_units: dict | None = None,
                        sort_by: str = "total", sort_reverse: bool = False) -> str:
    if time_units is None:
        time_units = get_column_time_units(results)
    res_copy = {k: dict(v) for k, v in results.items()}
    format_metric_columns(results=res_copy, col=RawCol.AST_CHECK_DUR, values_mode=values_mode,
                          highlight=highlight, time_unit=time_units.get(RawCol.AST_CHECK_DUR))
    format_metric_columns(results=res_copy, col=RawCol.CHECK_DUR, values_mode=values_mode,
                          highlight=highlight, time_unit=time_units.get(RawCol.CHECK_DUR))
    format_metric_columns(results=res_copy, col=RawCol.COMPILE_DUR, values_mode=values_mode,
                          highlight=highlight, time_unit=time_units.get(RawCol.COMPILE_DUR))
    format_metric_columns(results=res_copy, col=RawCol.CHECK_RSS, values_mode=values_mode,
                          highlight=highlight)
    format_metric_columns(results=res_copy, col=RawCol.BUILD_RSS, values_mode=values_mode,
                          highlight=highlight)
    format_metric_columns(results=res_copy, col=RawCol.OUTPUT_SIZE, values_mode=values_mode,
                          highlight=highlight)

    merged_results = merge_plain_and_templated_results(res_copy, values_mode=values_mode,
                                                       highlight=highlight)
    grouped_raw = {}
    for (l, t, c), r in results.items():
        grouped_raw.setdefault((l, c), {})[t] = r
    col_map = {
        "check": RawCol.CHECK_DUR,
        "compile": RawCol.COMPILE_DUR,
        "build": RawCol.BUILD_DUR,
        "run": RawCol.RUN_DUR,
        "check-rss": RawCol.CHECK_RSS,
        "build-rss": RawCol.BUILD_RSS,
        "output-size": RawCol.OUTPUT_SIZE,
        "size": RawCol.OUTPUT_SIZE,
    }
    norm_sort = str(sort_by).lower().replace("_", "-")

    def _skey(item):
        (l, c), m_row = item
        variants = grouped_raw.get((l, c), {})
        name = m_row[0].lower()
        if norm_sort in ("name", "lang", "language"):
            return (0, name)
        val = _extract_total(variants) if norm_sort in ("total", "build+run", "build-run", "time") else \
            (_extract_metric(variants, col_map[norm_sort]) if norm_sort in col_map else None)
        return (0, -val if sort_reverse else val, name) if val is not None else (1, 0, name)

    if norm_sort in ("name", "lang", "language"):
        sorted_rows = [it[1] for it in sorted(merged_results.items(), key=lambda it: it[1][0].lower(), reverse=sort_reverse)]
    else:
        sorted_rows = [it[1] for it in sorted(merged_results.items(), key=_skey)]

    table = PrettyTable()
    table.set_style(TableStyle.MARKDOWN)
    table.field_names = titles
    for row in sorted_rows:
        table.add_row(row)
    return table.get_string() + chr(10)


def markdown_table(titles: list[str], results: Results, values_mode: str = "absolute",
                   highlight: bool = False, sort_by: str = "total",
                   sort_reverse: bool = False) -> str:
    time_units = get_column_time_units(results) if results else {}
    if titles is None or (results and titles == table_titles(values_mode)):
        titles = table_titles(values_mode, results)
    tiered_results: dict[int, Results] = {1: {}, 2: {}, 3: {}}
    for key, row in results.items():
        lang, _, cexec = key
        tier = get_semantic_tier(str(lang), str(cexec))
        tiered_results[tier][key] = dict(row)

    nl = chr(10)
    sections = []
    for tier_id, title, desc in TIERS:
        t_res = tiered_results.get(tier_id)
        if not t_res:
            continue
        tbl = render_single_table(titles, t_res, values_mode=values_mode, highlight=highlight,
                                  time_units=time_units, sort_by=sort_by, sort_reverse=sort_reverse)
        legend = ""
        if any(k[1] for k in t_res):
            legend = "*Stacked cells: top = untemplated, bottom = templated (`-` = not available).*" + nl + nl
        sections.append("### " + title + nl + "*" + desc + "*" + nl + nl + legend + tbl)

    return (nl + nl).join(sections)
