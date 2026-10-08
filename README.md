# compiler-benchmark

Benchmarks compilation speeds, memory consumption (peak RSS), and binary output sizes across different programming languages and compilers.

### ⚠️ Scope & Methodology Notes

* **What this measures:** Raw front-end symbol ingestion, AST
  traversal, and unoptimized code-generation scaling under a massive,
  single translation unit consisting of synthetic arithmetic call
  chains.
* **Architectural tradeoffs:** Compilers with single-pass
  architectures (e.g., `tcc`) or minimal semantic models will
  naturally outperform multi-pass optimizing compilers (e.g., `rustc`,
  `ghc`, `swiftc`) that perform trait resolution, lifetime/borrow
  validation, or multi-stage IR lowering.
* **Synthetic vs. Real-world:** Real-world build times are heavily
  driven by header parsing (`#include`), package/module resolution,
  standard library footprint, and cross-crate/module parallelism, none
  of which are exercised by isolated arithmetic trees.

## Requirements

- Linux (tested on Arch Linux). CPU pinning uses `os.sched_setaffinity`; other POSIX systems may work with reduced functionality.
- Python 3.12 or later (the script uses `typing.override`).
- [`psutil`](https://pypi.org/project/psutil/) (installed automatically with `pip` on first run if missing).
- The `process_timer` helper module (providing `ProcessTimer`, used for RSS sampling) next to the `benchmark` script.
- At least one of the supported compilers in `PATH` (or in the directory given via `--path`). A subset of them can be installed via `./provision.sh`.

## Supported Languages and Compilers

### Native Ahead-of-Time (AOT) Compilers
- [Ada](https://en.wikipedia.org/wiki/Ada_(programming_language)) (using `gnat`)
- [C](https://en.wikipedia.org/wiki/C_(programming_language)) (using [`gcc`](https://gcc.gnu.org/), [`clang`](https://clang.llvm.org/), [`cproc`](https://github.com/michaelforney/cproc), [`cuik`](https://github.com/RealNeGate/Cuik/), [`tcc`](https://bellard.org/tcc/))
- [C++](https://isocpp.org/) (using [`g++`](https://gcc.gnu.org/), [`clang++`](https://clang.llvm.org/))
- [C3](https://c3-lang.org/) (using [`c3c`](https://github.com/c3lang/c3c))
- [Crystal](https://crystal-lang.org/) (using [`crystal`](https://crystal-lang.org/))
- [D](https://dlang.org/) (using [`dmd`](https://dlang.org/download.html), [`ldmd2`](https://github.com/ldc-developers/ldc), [`gdc`](https://gcc.gnu.org/wiki/GDC))
- [Fortran](https://gcc.gnu.org/wiki/GFortran) (using `gfortran`)
- [Go](https://golang.org/) (using `go`, `gccgo`)
- [Hare](https://harelang.org/) (using `hare`)
- [Haskell](https://www.haskell.org/) (using `ghc`)
- [Hylo](https://www.hylo-lang.org/) (using `hc`)
- [Mojo](https://www.modular.com/mojo) (using `mojo`)
- [Nim](https://nim-lang.org/) (using `nim`)
- [OCaml](https://ocaml.org/) (using `ocamlopt`)
- [Odin](https://odin-lang.org/) (using `odin`)
- [Pareas](https://github.com/Snektron/pareas) (using `pareas`)
- [Pascal](https://www.freepascal.org/) (using `fpc`)
- [Pony](https://www.ponylang.io/) (using `ponyc`)
- [Roc](https://www.roc-lang.org/) (using `roc`)
- [Rust](https://www.rust-lang.org/) (using `rustc`)
- [Swift](https://swift.org/) (using `swiftc`)
- [V](https://vlang.io/) (using `v`)
- [Vox](https://github.com/MrSmith33/vox) (using `vox`)
- [Zig](https://ziglang.org/) (using `zig`)
- [Dart](https://dart.dev/) (using `dart`)
- [SBCL](https://www.sbcl.org/) (using `sbcl`)
- [Guile](https://www.gnu.org/software/guile/) (using `guild`)

### Bytecode, VM, and JIT/Scripting Toolchains
- [C#](https://learn.microsoft.com/dotnet/csharp/) (using `csc` or `mcs`, executed via `mono`)
- [Java](https://www.oracle.com/java/) (using `javac`, executed via `java`)
- [Julia](https://julialang.org/) (using `julia`)
- [Lua](https://luajit.org/) (using `luajit`)
- [OCaml Bytecode](https://ocaml.org/) (using `ocamlc`, executed via `ocamlrun`)
- [Python](https://www.python.org/) (using `python3`, `python`, `pypy3`, `pypy`)
- [Scheme](https://cisco.github.io/ChezScheme/) (using `chez`, `scheme`)
- [TypeScript](https://www.typescriptlang.org/) (using `tsc`, executed via `node`)

### Support Matrix

Which operations and variants each language participates in. The *Tier* column controls which result table a compiler ends up in (see [Understanding Metrics and Table Output](#understanding-metrics-and-table-output)).

| Language | Compilers | Operations | Templated | Tier |
| :--- | :--- | :--- | :---: | :---: |
| Ada | `gnat` | check, build | – | 2 |
| C | `tcc`, `cuik`, `cproc` | check, compile, build | – | 1 |
| C | `gcc`, `clang` | check, compile, build | – | 2 |
| C++ | `g++`, `clang++` | check, compile, build | ✓ | 2 |
| C3 | `c3c` | check, compile, build | ✓ | 2 |
| C# | `mcs`, `csc` | check, build | – | 3 |
| Common Lisp | `sbcl` | check, compile, build | – | 3 |
| Crystal | `crystal` | check, build | ✓ | 3 |
| D | `dmd`, `ldmd2`, `gdc` | check, compile, build | ✓ | 2 |
| Dart | `dart` | check, compile, build | ✓ | 3 |
| Fortran | `gfortran` | check, compile, build | – | 2 |
| Go | `go`, `gccgo` | check, build | ✓ | 2 |
| Guile | `guild` | check, compile, build | – | 3 |
| Hare | `hare` | check, build | – | 2 |
| Haskell | `ghc` | check, build | ✓ | 3 |
| Hylo | `hc` | check, build | ✓ | 2 |
| Java | `javac` | check, build | – | 3 |
| Julia | `julia` | check, build | ✓ | 3 |
| Lua | `luajit` | check, compile, build | – | 3 |
| Mojo | `mojo` | build | – | 2 |
| Nim | `nim` | check, build | ✓ | 2 |
| OCaml | `ocamlopt`, `ocamlc` | check, build | – | 3 |
| Odin | `odin` | check, build | ✓ | 2 |
| Pareas | `pareas` | check, build | – | 2 |
| Pascal | `fpc` | check, compile, build | – | 2 |
| Pony | `ponyc` | check, build | – | 2 |
| Python | `python3`, `python`, `pypy3`, `pypy` | check, compile, build | ✓ | 3 |
| Roc | `roc` | check, build, run | – | 2 |
| Rust | `rustc` | check, build | ✓ | 2 |
| Scheme | `chez`, `scheme` | check, compile, build | – | 3 |
| Swift | `swiftc` | check, build | ✓ | 2 |
| TypeScript | `tsc` | check, compile, build | ✓ | 3 |
| V | `v` | check, build | ✓ | 2 |
| Vox | `vox` | check, build | ✓ | 2 |
| Zig | `zig` | ast-check, check, compile, build | ✓ | 2 |

### Compiler Discovery

- Executables are looked up with `which` in `PATH`, or in the directory given by `--path`.
- For compilers that ship with versioned names (`gcc`, `g++`, `clang`, `clang++`, `gfortran`, `gnat`, `gccgo`), the unversioned binary as well as `-5` to `-19` suffixed binaries (e.g. `gcc-15`) are discovered and benchmarked as separate rows.
- Language names given to `--languages` are case-insensitive and a few aliases are accepted (e.g. `ts`/`tsc` for TypeScript, `fpc` for Pascal, `ghc` for Haskell, `gfortran` for Fortran, `guild` for Guile, `luajit` for Lua, `chez` for Scheme, and `lisp`/`sbcl`/`commonlisp` for Common Lisp).
- When `rustup` is available, Rust is benchmarked on both the `stable` and `nightly` channels. Note that this switches your `rustup` default toolchain while the benchmark runs.
- Compiler versions are probed automatically (e.g. `--version`, `-v`, `version`) and shown in the table's first column.

---

## Benchmark Operations

The benchmark supports up to five distinct operations per compiler target:

| Operation | CLI Flag | Description |
| :--- | :--- | :--- |
| **AST Check** | `ast-check` | Syntax / AST validation only (currently only `zig ast-check`). Not part of the default operations; enable with `--ast-check` or `--ops=ast-check,...`. |
| **Check** | `check` | Semantic validation and type checking without machine code emission (e.g. `-fsyntax-only`, `--emit=metadata`, `-typecheck`, `--no-codegen`). |
| **Compile** | `compile` | Compiles to object code or bytecode without linking (e.g. `-c`, `py_compile`, or `compile-only`). |
| **Build** | `build` | Full end-to-end compilation and linking producing an executable binary (or bytecode/script artifact for VM languages). |
| **Run** | `run` | Measures execution time of the built artifact over `--run-count` runs. Not a standalone task: the run is performed automatically right after each successful `build`. |

The default operations are `check`, `compile`, `build` and `run`. An operation is only executed for languages that support it (see the [Support Matrix](#support-matrix)); unsupported combinations are simply skipped.

---

## How It Works

### Running the Benchmark

Run the suite with default parameters:

```bash
./benchmark
```

Configure function sizing, repetition counts, and operations:

```bash
./benchmark \
    --function-count=$FUNCTION_COUNT \
    --function-depth=$FUNCTION_DEPTH \
    --run-count=5
```

or using short aliases:

```bash
./benchmark --fc=200 --fd=200 --rc=5 --ops=check,build
```

Filter specific languages or explicit compiler executables:

```bash
./benchmark --languages=C:tcc,C:gcc,C++,D:dmd,D:ldmd2,D:gdc,Rust
```

Include Zig's AST check and show relative numbers with the best value highlighted:

```bash
./benchmark --langs=Zig,C:tcc --ast-check --values=both --highlight-min
```

### CLI Arguments Reference

| Option | Short | Default | Description |
| :--- | :--- | :--- | :--- |
| `--languages` | `--langs` | All supported (that are found in `PATH`) | Comma-separated list of languages and optional compilers (`<Lang>:<exe>`). Unknown languages and missing compiler binaries are reported with a warning. |
| `--operations` | `--ops` | `check,compile,build,run` | Comma-separated operations (`ast-check`, `check`, `compile`, `build`, `run`). |
| `--ast-check` | | `false` | Also run the AST syntax check (e.g. `zig ast-check`) in addition to the selected operations. |
| `--function-count` | `--fc` | `200` | Number of top-level function call chains generated. |
| `--function-depth` | `--fd` | `200` | Nesting call depth per chain (total functions = `fc * fd`). |
| `--run-count` | `--rc` | `10` | Repetitions per compilation step (minimum time recorded). |
| `--sample-rate` | `--sr` | `100` | Memory sampling frequency (samples/sec) for peak RSS tracking. |
| `--values` | `--val` | `absolute` | Display mode: `absolute`, `relative` (normalized to best), or `both`. |
| `--relative` | `--rel` | `false` | Shortcut for `--values=relative`. |
| `--highlight-min` | `--hl` | `false` | Highlights the lowest (best) metric in each column with HTML badges (applies in every `--values` mode). |
| `--path` | | `None` | Custom search path for locating compiler binaries. |
| `--verbose` | `-v` | `false` | Verbose logging (source generation and per-operation timings). |
| `--progress` | `--progress-format` | `auto` | Progress display: `auto` (tree on capable terminals, line otherwise, none when not a TTY), `tree`, `line`, or `none`. |

### Parallel Execution Architecture

`benchmark` automatically scales across the available CPU cores:
- Distributes individual benchmark tasks (one per language, operation, templated variant and compiler runner) into a `multiprocessing.Pool`.
- Detects hybrid CPUs (Intel P/E cores via the PMU topology, ARM big.LITTLE via `cpu_capacity`, per-core maximum frequency, and Apple Silicon performance levels) and, if found, uses **only the performance cores**, one worker per core. On homogeneous CPUs it uses all available cores minus two (at least one) to leave headroom for the system.
- Pins each worker process to a dedicated CPU core via `os.sched_setaffinity` to avoid core-hopping noise.
- Generates sources in a temporary root directory (`/tmp/generated_*`) and isolates compiler scratchpads in per-process directories (`proc_<PID>/<lang>/`).
- Removes a task's scratch directory when it succeeded; if a compiler printed output or returned a non-zero exit code, the directory is kept for inspection and a warning with the command line, stdout and stderr is printed.
- Cleans up temporary files and empty directories upon benchmark completion or exit (including `Ctrl-C`).
- Shows live progress (tree or single line) with the currently active tasks and their elapsed times, unless disabled with `--progress=none` or when output is not a terminal.

---

## Understanding Metrics and Table Output

Results are printed as Markdown tables, split into three tiers according to the architecture of the compiler:

| Tier | Contents |
| :--- | :--- |
| **Tier 1: Single-Pass / Minimalist Compilers** | `tcc`, `cuik`, `cproc`: no SSA optimization, no borrow checking, trivial type systems, instant code emission. |
| **Tier 2: Modern Systems Languages (Ahead-of-Time)** | Full type inference, monomorphization/generics, semantic safety, module systems. |
| **Tier 3: Managed & VM / JIT / Scripting** | Bytecode emission, runtime metadata, GC runtimes. |

Rows within a tier are sorted alphabetically. Relative values and highlighting are computed per tier table.

All metric columns in the output Markdown table are normalized per generated function:

$$\text{Total Functions} = \text{function\_count} \times \text{function\_depth}$$

For languages with a safety cap (see below) the capped sizes are used for normalization.

- **`Total (Build + Run) [us/f]`**: Minimum build time plus minimum run time per function, shown as `total (build+run)` (e.g. `2.6 (...)`-style cells such as `115.6 (2.6+113.0)`). `N/A` for toolchains that have no build step or whose artifact isn't executed.
- **`Check [us/f]`**, **`Compile [us/f]`**: Minimum execution duration divided by total functions (`args.function_count * args.function_depth`). If AST checking is enabled and supported (e.g. Zig), its result is shown on a second line (`<br>`) inside the **Check** cell.
- **`Check RSS [kB/f]`**, **`Build RSS [kB/f]`**: Maximum resident set size (sampled at `--sample-rate` via `psutil` / process timer) in kilobytes divided by total functions. Cells show `sampling error` or `missing` when memory could not be sampled.
- **`Output Size [B/f]`**: Stripped binary disk footprint in bytes divided by total functions (native machine-code binaries only: ELF, Mach-O or PE; `N/A` for bytecode/script artifacts).

The time unit of the Check, Compile and Total columns is chosen automatically per column (`s/f`, `ms/f`, `us/f` or `ns/f`, based on the median value) and shown in the column header. In `--values=relative` mode the header unit is replaced by `[x]`; in `--values=both` mode each cell shows `absolute (relative)`.

> **Note:** The sample run in the section below was produced with an earlier table layout that lists *Build* and *Run* as separate columns. The current version reports them together in the `Total (Build + Run)` column.

### Merged Plain and Templated Results

Rather than displaying separate rows, plain and templated/generic results are merged into each metric cell as:

$$\langle\text{plain}\rangle,\ \langle\text{templated}\rangle$$

- A dash `-` indicates that the corresponding variant does not apply or was not evaluated (e.g. `1897.3, -` for non-generic languages or `-, 120.4` for template-only tests).
- `N/A` is shown when neither variant produced a value (e.g. the operation is unsupported or the compiler failed).
- When `--highlight-min` is active, the best plain value and best templated value are highlighted independently within their respective cell halves. Highlighting applies to the Check, Compile, RSS and Output Size columns.

---

## Generics & Synthetic Code Structure

For languages supporting generics, the benchmark emits an un-templated test file `main_<run>.<ext>` and a templated test file `main_t_<run>.<ext>` (one file per repetition). In the templated file, all functions (except `main`) are generic and instantiated for the language's 64-bit scalar type. A few languages need different layouts: Ada uses `main.adb`/`main_t.adb` (the file name must match the unit) and Pony places every generated program in its own package subdirectory.

### Semantic Checking Differences

GCC and Clang don't perform all semantic checks for C++ (because it's too costly). This is in contrast to D's and Rust's compilers that perform all of them.

### Sample Generated Code (`C`, 3 functions, depth 2)

Running:

```bash
./benchmark --function-count=3 --function-depth=2 --run-count=5
```

produces `/tmp/generated_<random>/proc_<PID>/c/main_0.c` (removed again after a successful run unless the compiler reported problems):

```c
long add_long_n0_h0(long x) { return x + 15440; }
long add_long_n0(long x) { return x + add_long_n0_h0(x) + 95485; }

long add_long_n1_h0(long x) { return x + 37523; }
long add_long_n1(long x) { return x + add_long_n1_h0(x) + 92492; }

long add_long_n2_h0(long x) { return x + 39239; }
long add_long_n2(long x) { return x + add_long_n2_h0(x) + 12248; }

int main(void) {
    long long_sum = 0;
    long_sum += add_long_n0(0);
    long_sum += add_long_n1(1);
    long_sum += add_long_n2(2);
    return long_sum;
}
```

### Compiler Object Caches

The numerical constants are randomized using a new seed upon every call. This makes it impossible for any compiler to utilize any caching mechanism upon successive calls with same flags that affect the source generation. The purpose of this is to make the comparison between compilers with and without (different levels of) caching more fair.

The caching of the Go reference compiler `go`, for instance, is effectively disabled by this randomization. The Hare cache directory (`HARECACHE`) is additionally wiped before each Hare benchmark.

---

## Compiler Constraints and Safety Caps

Because synthetic code generators create tens of thousands of deeply nested symbols, certain compilers encounter internal limits. The benchmark automatically enforces the following stability caps (they only affect the language in question; other languages keep the requested size):

- **Both OCaml and Julia** scale poorly on deeply nested functions with large synthetic function counts, so an explicit limit of $200 \times 200$ is enforced once `function_count * function_depth` reaches $10{,}000$.
- **Nim**: The Nim compiler has a hard limit of 50 recursive generic instantiations, so `--function-depth` is automatically truncated down to `50`.
- **Java**: Capped to $100 \times 100$ ($10{,}000$ functions) when more functions are requested, to avoid exceeding the JVM $65{,}535$ constant pool entry limit per class file.
- **Lua / LuaJIT**: Capped to $150 \times 150$ when more than $20{,}000$ functions are requested, to avoid exceeding the LuaJIT bytecode chunk constant table limit ($65{,}536$).
- **Cuik**: Function count and depth are each capped to $100$ due to compiler stability limits.

A warning is printed whenever a cap (other than OCaml/Julia) is applied.

---

## Adding a Language

Adding a language only requires inserting one contiguous block into the *LANGUAGE BLOCKS* section of `benchmark`; nothing else needs to change. A block consists of:

1. one or more `bm_<Lang>` runner functions that invoke the compiler(s) via `benchmark_compiler_op`, and
2. a single `register_language(LangSupport(...))` call describing everything else: compiler executables, file extension, 64-bit integer type, supported operations and templated variants, version probing (`VersionSpec`), reporting tier, `--languages` aliases, argument limits, and all source-code generation hooks (prefix, function emitter, `main` header, variable declarations, calls, postfix) plus optional quirks (custom program directory, source file name, section ordering, or compiler command line).

The generic engine only talks to languages through `LangSupport`.

---

## AMD Ryzen AI 7 350 (8+8) @ 5.09 GHz

The output on Arch Linux (as of 2026-09) for the sample call

    ./benchmark

results in the following table (copied from the output at the end).

### Tier 1: Single-Pass / Minimalist Compilers
*No SSA optimization, no borrow checking, trivial type systems, instant code emission.*

| Language (Exec)  | Total (Build + Run) [us/f] | Check [us/f] | Compile [us/f] | Check RSS [kB/f] | Build RSS [kB/f] | Output Size [B/f] |
| :--------------: | :------------------------: | :----------: | :------------: | :--------------: | :--------------: | :---------------: |
| C (cproc)        | 86 (86+0.21)               | 9.5          | 70.8           | 2.4              | 2.8              | 90.1              |
| C (cuik ~master) | 70 (70+0.21)               | 4.3          | 39.7           | 3.2              | 52.6             | 114.4             |
| C (tcc 0.9.28rc) | 3 (2+0.21)                 | 2.1          | 2.3            | 1.1              | 1.1              | 90.1              |


### Tier 2: Modern Systems Languages (Ahead-of-Time)
*Full type inference, monomorphization/generics, semantic safety, module systems.*

*Stacked cells: top = untemplated, bottom = templated (`-` = not available).*

| Language (Exec)                   | Total (Build + Run) [us/f]       | Check [us/f] | Compile [us/f] | Check RSS [kB/f] | Build RSS [kB/f]   | Output Size [B/f] |
| :-------------------------------: | :------------------------------: | :----------: | :------------: | :--------------: | :----------------: | :---------------: |
| Ada (gnat 16.2.1)                 | 1186 (1185+0.42)                 | 37.4         | N/A            | 19.8             | 51.7               | 263.0             |
| C (clang 23.1.1)                  | 106 (106+0.19)                   | 13.6         | 79.2           | 3.3              | 6.9                | 146.1             |
| C (gcc 16.2.1)                    | 455 (455+0.20)                   | 12.1         | 439.7          | 3.9              | 17.8               | 121.1             |
| C (gcc-15 15.3.0)                 | 504 (504+0.19)                   | 12.0         | 199.8          | 3.7              | 17.2               | 121.1             |
| C++ (clang++ 23.1.1)              | 106 (105+0.21)<br>112 (112+0.10)     | 17.9<br>29.5     | 82.9<br>122.1      | 3.6<br>6.1           | 9.8<br>13.0            | 151.1<br>142.2        |
| C++ (g++ 16.2.1)                  | 486 (486+0.21)<br>448 (448+0.10)     | 34.0<br>77.4     | 421.7<br>537.7     | 7.6<br>11.5          | 18.1<br>23.7           | 126.1<br>127.2        |
| C++ (g++-15 15.3.0)               | 445 (445+0.20)<br>520 (520+0.10)     | 28.3<br>69.8     | 216.8<br>589.5     | 7.0<br>10.7          | 17.4<br>23.0           | 126.1<br>127.2        |
| C3 (c3c 0.8.5)                    | 133 (133+0.21)<br>229 (229+0.21)     | 16.6<br>96.4     | 115.9<br>221.2     | 6.2<br>7.7           | 17.1<br>22.7           | 338.8<br>418.5        |
| D (dmd 2.113.0-ecca64b)           | 14 (14+0.21)<br>19 (19+0.05)         | 4.3<br>10.9      | 10.9<br>31.2       | 4.9<br>11.7          | 15.3<br>23.9           | 178.5<br>194.5        |
| D (gdc 16.2.1)                    | 483 (483+0.21)<br>402 (401+0.10)     | 16.4<br>29.5     | 501.2<br>494.5     | 6.5<br>15.9          | 24.0<br>sampling error | 178.3<br>182.4        |
| D (ldmd2 1.43.0)                  | 96 (96+0.21)<br>82 (82+0.10)         | 5.4<br>13.5      | 73.3<br>92.4       | 7.7<br>18.0          | 16.3<br>32.6           | 168.9<br>163.0        |
| Fortran (gfortran 16.2.1)         | 1240 (1240+0.20)                 | 355.4        | 1254.7         | 22.0             | 35.6               | 140.8             |
| Go (go 1.27.1-X:nodwarf5)         | 447 (447+0.10)<br>437 (437+0.09)     | 55.1<br>52.5     | N/A            | 10.7<br>10.5         | 32.7<br>31.6           | 188.9<br>188.9        |
| Hare (hare 0.26.0.1)              | 152 (152+0.05)                   | 91.3         | N/A            | 110.8            | 110.8              | 222.0             |
| Nim (nim 2.2.12)                  | 691 (691+0.20)<br>759 (758+0.20)     | 83.6<br>145.7    | N/A            | 7.6<br>15.2          | 43.8<br>50.4           | 178.0<br>181.4        |
| Odin (odin dev-2026-09:a2fb372b7) | 125 (125+0.10)<br>99 (99+0.09)       | 20.7<br>34.1     | N/A            | 20.4<br>32.1         | 35.8<br>51.5           | 112.6<br>132.6        |
| Pascal (fpc 3.2.2)                | 138 (138+0.21)                   | 97.5         | 104.5          | 17.9             | 24.4               | 68.8              |
| Pony (ponyc 0.72.1-de5eddd)       | 1057 (1057+0.0)                  | 631.3        | N/A            | 198.0            | 282.3              | 804.8             |
| Roc (roc compiler)                | 328 (165+163.1)                  | 91.7         | N/A            | 47.0             | 44.2               | 431.4             |
| Rust (rustc 1.100.0-nightly)      | 185 (185+0.19)<br>214 (214+0.15)     | 87.0<br>130.9    | N/A            | 16.2<br>15.3         | 32.0<br>27.1           | 360.4<br>300.3        |
| Swift (swiftc 6.4)                | 1086 (1085+0.83)<br>2455 (2454+0.80) | 637.4<br>1330.2  | N/A            | 33.1<br>31.4         | 59.9<br>72.1           | 208.5<br>531.3        |
| V (v 0.5.0)                       | 545 (544+0.20)<br>1385 (1385+0.14)   | 10.2<br>843.8    | N/A            | 10.2<br>181.5        | 36.1<br>200.8          | 132.3<br>138.3        |
| Zig (zig 0.18.0-dev.35+5e754304d) | 102 (102+0.20)<br>95 (95+0.21)       | 22.2<br>33.2     | 61.0<br>106.5      | 4.6<br>5.3           | 9.5<br>12.7            | 1503.4<br>1422.5      |


### Tier 3: Managed & VM / JIT / Scripting
*Bytecode emission, runtime metadata, GC runtimes.*

*Stacked cells: top = untemplated, bottom = templated (`-` = not available).*

| Language (Exec)             | Total (Build + Run) [us/f]     | Check [us/f] | Compile [us/f] | Check RSS [kB/f] | Build RSS [kB/f] | Output Size [B/f] |
| :-------------------------: | :----------------------------: | :----------: | :------------: | :--------------: | :--------------: | :---------------: |
| C# (csc 3.9.0-6.21124.20)   | 211 (202+9.1)                  | 47.4         | N/A            | 7.6              | 10.1             | N/A               |
| C# (mcs 6.12.0.0)           | 55 (38+16.6)                   | 36.9         | N/A            | 5.2              | 5.1              | N/A               |
| Common Lisp (sbcl 2.6.9)    | 546 (545+0.41)                 | 495.2        | 483.8          | 4.2              | 5.6              | 1481.3            |
| Crystal (crystal 1.21.1)    | 406 (406+0.40)<br>379 (378+0.41)   | 129.1<br>139.7   | N/A            | 33.0<br>31.0         | 83.9<br>83.3         | 384.9<br>384.9        |
| Dart (dart 3.13.5)          | 309 (309+0.40)<br>434 (434+0.41)   | 189.5<br>265.1   | 296.6<br>456.9     | 13.4<br>15.7         | 10.4<br>11.2         | 430.6<br>500.3        |
| Guile (guild 3.0.11)        | 7964 (7957+6.6)                | 8503.1       | 8624.4         | 48.1             | 50.9             | N/A               |
| Haskell (ghc 9.6.7)         | 3752 (3750+1.6)<br>4387 (4386+1.6) | 2434.0<br>2610.7 | N/A            | 64.3<br>59.2         | 81.6<br>88.5         | 657.3<br>616.3        |
| Java (javac 27)             | 441 (430+11.5)                 | 169.4        | N/A            | 19.0             | 25.0             | N/A               |
| Julia (julia 1.14.0-DEV)    | 496 (496+0.0)<br>456 (456+0.0)     | 17.6<br>13.2     | N/A            | 8.7<br>8.6           | 13.0<br>12.4         | N/A               |
| Lua (luajit 2.1.1788856981) | 4 (4+0.72)                     | 3.3          | 3.4            | 0.8              | 0.8              | N/A               |
| OCaml (ocamlc 5.5.0)        | 149 (149+0.05)                 | 128.3        | N/A            | 16.7             | 20.4             | N/A               |
| OCaml (ocamlopt 5.5.0)      | 480 (480+0.21)                 | 120.9        | N/A            | 16.8             | 52.3             | 579.1             |
| Python (pypy3 3.12.14)      | 64 (55+9.1)<br>69 (59+10.4)        | 47.0<br>57.5     | 53.3<br>57.0       | 11.2<br>12.3         | 13.0<br>14.2         | N/A               |
| Python (python 3.14.7)      | 34 (31+2.9)<br>47 (42+5.4)         | 28.6<br>42.4     | 30.2<br>40.5       | 11.2<br>14.3         | 11.3<br>14.3         | N/A               |
| Python (python3 3.14.7)     | 32 (29+2.9)<br>48 (43+5.4)         | 27.2<br>41.2     | 31.3<br>39.4       | 11.2<br>14.3         | 11.3<br>14.3         | N/A               |
| Scheme (chez 10.3.0)        | 262 (245+16.6)                 | 8.4          | 243.3          | 1.3              | 11.9             | N/A               |
| TypeScript (tsc 6.0.3)      | 455 (443+11.5)<br>502 (490+11.5)   | 386.2<br>452.7   | 478.3<br>495.3     | 39.1<br>40.6         | 40.6<br>43.6         | N/A               |

## Conclusions (from sample run shown above)

The Tiny C Compiler (TCC) (`tcc`) is by a large margin the fastest
compiler in build speed, followed by the C compiler Cuik and D's
`dmd`. TCC's vastly superior build speed stems from its single-pass
code-generation architecture: because C relies on explicit forward
declarations, the compiler does not need multi-pass symbol resolution,
effectively limiting AST parsing, memory allocation, and code
generation scope to a single function at a time.

The performance of both GCC and Clang sometimes worsen with a newer
release.

Both OCaml and Julia scale poorly on deeply nested functions with
large synthetic function counts, an explicit maximum limit is
therefore enforced. Moreover, the Nim compiler has a hard limit of 50
recursive generic instantiations so therefore `--function-depth` is
automatically truncated down to 50.

---

## References

- [Go compilation times compared to C++, D, Rust, Pascal (cross-posted)](https://www.reddit.com/r/golang/comments/55k7n4/go_compilation_times_compared_to_c_d_rust_pascal/)
- [LanguageCompilationSpeed](https://wiki.alopex.li/LanguageCompilationSpeed)
