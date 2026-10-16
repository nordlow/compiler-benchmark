# Benchmarking Compilers: DMD D is Fastest at Cold Compilation - By Far!

Benchmarking compilation throughput, peak memory (RSS), and binary
density across 30+ compilers on massive arithmetic translation
units. The current methodology represents one out of many ways to
exercise the compiler; suggestions for extended or alternative
approaches are most welcome.

---

### ⚡ Highlights & Key Findings (AMD Ryzen AI 7 350)

* **DMD’s Custom Backend Outperforms by 6×–38× vs. C/C++ (and Up to
  120× Across Systems Languages):** Digital Mars D (`dmd`) achieves
  **13 µs/function** (`µs/f` in table) (full semantic check + native
  codegen + linking), easily outpacing minimalist C compilers like
  `cuik` and `cproc`. Crucially, DMD dramatically outperforms modern
  languages marketed for fast iteration—**even when testing Zig using
  its custom, non-LLVM backend**. The major caveat is that Zig
  features an experimental, built-in (incremental) build server mode
  that keeps the compiler resident in memory to patch binaries
  in-place—a paradigm shift that DMD completely lacks, and one that
  fundamentally changes inner-loop performance when active. However,
  because not all workflows can leverage a persistent daemon (e.g.,
  CI/CD pipelines, clean rebuilds, batch scripts, and integration with
  external build systems), DMD's sheer cold-compilation throughput
  remains unmatched. In particular, the rise of agentic coding
  workflows—where AI agents continuously spin up ephemeral
  environments, perform clean checkouts, and execute rapid test-refine
  loops without warm caches—makes this cold-start advantage
  increasingly vital. At the same time, cross-toolchain D benchmarks
  cleanly isolate the backend tax: all LLVM-based compilers are at
  least **~6× slower** slower proving that without architectural
  gimmicks or LLVM bloat, Walter Bright solved batch build latency
  decades ago. As a side-note, DMD compiles itself in debug mode in
  2.5s on this same machine.
* **TCC Leads Single-Pass C:** The Tiny C Compiler (`tcc`) streams
  machine code at **3 µs/f**, remaining the undisputed speed champion
  for raw C ingestion.
* **Modern Systems Throughput:** After D, `C` (Clang) and `Zig` lead the
  ahead-of-time pack at **80–89 µs/f**, with `Odin` (105 µs/f) close
  behind, while `Rust` (184 µs/f) significantly outpaces GCC-based
  C/C++ (~441–483 µs/f).
* **The Monomorphization Penalty:** Both `Zig` (+7%) and `Rust` (+3%)
  demonstrate near-zero generic build overhead. Compilers like `C3` (1.7×),
  `Swift` (1.9×), and `V` (3.0×) suffer noticeable monomorphization penalties,
  whereas several compilers (`ldmd2`, `Odin`, `Nim`, `Crystal`, `Julia`)
  actually build templated scalar code faster than non-generic equivalents.
* **Untyped vs. Typed Speed:** LuaJIT emits bytecode in 3.3 µs/f (5 µs/f
  Total including execution), but performs zero compile-time type
  verification or linking—making DMD's fully-typed, native-linked 13 µs/f
  an extraordinary engineering contrast.

---

## AMD Ryzen AI 7 350 (8+8) @ 5.09 GHz

The output on Arch Linux (as of 2026-09) for the sample call
`./benchmark` results in the following tables:

### Modern Systems Languages (Ahead-of-Time)
*Full type inference, monomorphization/generics, semantic safety, module systems.*

*Stacked cells: top = untemplated, bottom = templated (`-` = not available).*

|          Language (Exec)           |      Total=Build+Run [µs/f]      |   Check [µs/f]  | Compile [µs/f] | Check RSS [kB/f] |    Build RSS [kB/f]    | Output Size [B/f] |
| :--------------------------------: | :------------------------------: | :-------------: | :------------: | :--------------: | :--------------------: | :---------------: |
|      D (dmd 2.113.0-bf2012d)       |     13=13+0.20<br>18=17+0.05     |    4.3<br>9.3   |  7.1<br>17.8   |   4.7<br>12.0    |      15.7<br>24.0      |   178.5<br>194.5  |
|          C (clang 23.1.1)          |            80=80+0.20            |       13.7      |      74.3      |       3.3        |          10.0          |       146.1       |
|          D (ldmd2 1.43.0)          |     82=82+0.21<br>74=74+0.05     |   5.6<br>15.0   |  39.1<br>85.8  |   7.6<br>17.4    |      19.0<br>32.2      |   168.9<br>163.0  |
|        C++ (clang++ 23.1.1)        |    84=84+0.21<br>112=112+0.10    |   17.4<br>28.6  | 90.6<br>102.6  |    3.6<br>6.1    |      10.1<br>13.0      |   151.1<br>142.2  |
| Zig (zig 0.18.0-dev.131+41f885830) |     89=89+0.20<br>95=95+0.20     |   22.6<br>24.4  |  88.9<br>97.3  |    4.5<br>5.5    |      9.6<br>12.7       |  1505.6<br>1423.6 |
| Odin (odin dev-2026-10:84bc3fc21)  |    105=105+0.10<br>99=99+0.05    |   14.6<br>23.1  |      N/A       |   15.9<br>29.9   |      34.1<br>51.5      |   112.6<br>132.7  |
|           C3 (c3c 0.8.5)           |   122=122+0.21<br>208=208+0.19   |   15.6<br>86.8  | 121.9<br>210.2 |    6.2<br>7.7    |      17.9<br>23.0      |   338.8<br>418.5  |
|         Pascal (fpc 3.2.2)         |           128=128+0.20           |       96.9      |     100.3      |       17.9       |          24.5          |        68.8       |
|        Hare (hare 0.26.0.1)        |           146=146+0.05           |      102.9      |      N/A       |      110.8       |         110.8          |       222.0       |
|    Rust (rustc 1.100.0-nightly)    |   184=184+0.21<br>190=190+0.19   |  90.6<br>113.9  |      N/A       |   16.2<br>17.7   |      32.0<br>30.1      |   360.4<br>300.3  |
|         Roc (roc compiler)         |          317=203+113.6           |       89.0      |      N/A       |       39.4       |          44.9          |       431.4       |
|            V (v 0.5.0)             |  395=395+0.21<br>1190=1189+0.21  |   9.6<br>773.6  |      N/A       |  10.2<br>181.7   |     36.2<br>202.9      |   132.3<br>138.3  |
|     Go (go 1.27.2-X:nodwarf5)      |   403=403+0.10<br>468=468+0.10   |   53.8<br>56.7  |      N/A       |   10.6<br>10.5   |      31.8<br>32.3      |   188.9<br>188.9  |
|           D (gdc 16.2.1)           |   432=432+0.20<br>486=486+0.05   |   15.0<br>30.9  | 410.9<br>452.5 |   6.5<br>15.9    |      24.0<br>33.9      |   178.3<br>182.4  |
|           C (gcc 16.2.1)           |           441=441+0.21           |       11.7      |     374.3      |       3.9        |          17.8          |       121.1       |
|         C (gcc-15 15.3.0)          |           441=441+0.10           |       11.5      |     229.3      |       3.7        |          17.1          |       121.1       |
|        C++ (g++-15 15.3.0)         |   461=461+0.20<br>487=487+0.09   |   27.1<br>64.7  | 201.3<br>537.1 |   7.0<br>10.7    |      17.4<br>23.7      |   126.1<br>127.2  |
|          C++ (g++ 16.2.1)          |   483=483+0.21<br>548=548+0.10   |   33.6<br>76.3  | 427.3<br>480.5 |   7.6<br>11.5    |      18.3<br>23.7      |   126.1<br>127.2  |
|          Nim (nim 2.2.12)          |   661=661+0.21<br>542=541+0.20   |  83.7<br>124.6  |      N/A       |   7.6<br>15.3    | 43.2<br>sampling error |   178.0<br>181.4  |
|    Pony (ponyc 0.72.1-de5eddd)     |           903=903+0.0            |      586.7      |      N/A       |      198.2       |         281.5          |       804.8       |
|         Ada (gnat 16.2.1)          |           957=957+0.41           |       32.3      |      N/A       |       19.8       |          51.7          |       263.0       |
|     Fortran (gfortran 16.2.1)      |          1076=1076+0.20          |      566.3      |     1081.2     |       22.0       |          37.7          |       140.8       |
|         Swift (swiftc 6.4)         | 1167=1167+0.82<br>2175=2175+0.82 | 621.9<br>1272.8 |      N/A       |   33.4<br>36.6   |      60.2<br>75.1      |   208.5<br>531.3  |


### Single-Pass / Minimalist Compilers
*No SSA optimization, no borrow checking, trivial type systems, instant code emission.*

| Language (Exec)  | Total=Build+Run [µs/f] | Check [µs/f] | Compile [µs/f] | Check RSS [kB/f] | Build RSS [kB/f] | Output Size [B/f] |
| :--------------: | :--------------------: | :----------: | :------------: | :--------------: | :--------------: | :---------------: |
| C (tcc 0.9.28rc) |        3=3+0.21        |     2.0      |      2.0       |       1.0        |       0.7        |        90.1       |
| C (cuik ~master) |       51=51+0.20       |     3.7      |      38.4      |       3.2        |       71.5       |       114.4       |
|    C (cproc)     |       80=79+0.20       |     8.9      |      69.1      |       2.4        |       3.6        |        90.1       |
| Forth (gforth 0.7.3) |       15=15+0.39       |     6.7      |      15.3      |       0.5        |       2.0        |        N/A        |


### Managed & VM / JIT / Scripting
*Bytecode emission, runtime metadata, GC runtimes.*

*Stacked cells: top = untemplated, bottom = templated (`-` = not available).*

|        Language (Exec)        |     Total=Build+Run [µs/f]     |   Check [µs/f]   | Compile [µs/f] | Check RSS [kB/f] |    Build RSS [kB/f]    | Output Size [B/f] |
| :---------------------------: | :----------------------------: | :--------------: | :------------: | :--------------: | :--------------------: | :---------------: |
|  Lua (luajit 2.1.1788856981)  |            5=3+1.4             |       3.6        |      3.3       |       0.7        |          0.7           |        N/A        |
|    Python (python3 3.14.8)    |     32=29+2.9<br>48=43+5.4     |   28.0<br>39.9   |  26.5<br>39.3  |   11.2<br>14.3   |      11.3<br>14.3      |        N/A        |
| Python (python3.15 3.15.0rc3) |     39=37+2.9<br>57=51+6.6     |   35.0<br>52.8   |  33.2<br>49.9  |   11.3<br>14.3   |      11.3<br>14.5      |        N/A        |
|       C# (mcs 6.12.0.0)       |           50=35+15.4           |       33.8       |      N/A       |       5.0        |          5.2           |        N/A        |
|     Python (pypy3 3.12.14)    |     63=54+9.1<br>64=55+9.1     |   45.6<br>57.2   |  48.4<br>54.6  |   11.2<br>12.3   |      13.0<br>14.5      |        N/A        |
|      OCaml (ocamlc 5.5.0)     |          137=137+0.05          |      120.3       |      N/A       |       16.8       |          20.4          |        N/A        |
|   Emacs-Lisp (emacs 32.0.50)  |          166=149+17.2          |      141.4       |     151.3      |       8.5        |          8.5           |        N/A        |
|   C# (csc 3.9.0-6.21124.20)   |          194=186+7.9           |       47.4       |      N/A       |       7.7        |          10.0          |        N/A        |
|      Scheme (chez 10.3.0)     |          262=247+15.4          |       8.2        |     287.5      |       1.4        |          11.9          |        N/A        |
|       Dart (dart 3.13.5)      |  298=297+0.39<br>427=427+0.41  |  182.5<br>248.8  | 295.0<br>437.7 |   13.1<br>15.7   |      10.4<br>11.0      |   430.6<br>500.3  |
|    Crystal (crystal 1.22.0)   |  366=365+0.41<br>350=349+0.41  |  123.6<br>122.5  |      N/A       |   32.1<br>30.8   | sampling error<br>79.4 |   386.6<br>386.6  |
|        Java (javac 27)        |          398=387+11.5          |      178.0       |      N/A       |       19.8       |          25.6          |        N/A        |
|     TypeScript (tsc 6.0.3)    |  443=432+11.5<br>474=463+11.4  |  380.1<br>435.5  | 466.9<br>489.4 |   39.5<br>42.1   |      40.3<br>44.4      |        N/A        |
|    Julia (julia 1.14.0-DEV)   |   523=523+0.0<br>444=444+0.0   |   16.6<br>13.5   |      N/A       |    8.8<br>8.7    |      12.1<br>12.4      |        N/A        |
|     OCaml (ocamlopt 5.5.0)    |          527=527+0.21          |      112.7       |      N/A       |       16.8       |          52.4          |       579.1       |
|    Common-Lisp (sbcl 2.6.9)   |          536=536+0.41          |      462.2       |     481.0      |       4.3        |          5.6           |       1481.3      |
|     F# (dotnet 14.0.112.0)    |         1994=1994+0.0          |      1164.1      |      N/A       |       43.9       |          61.3          |        N/A        |
|      Haskell (ghc 9.6.7)      | 3823=3821+1.6<br>4138=4136+1.6 | 2272.5<br>2277.9 |      N/A       |   62.6<br>63.9   | 81.5<br>sampling error |   657.3<br>616.3  |
|    Kotlin (kotlinc 2.4.21)    |         4446=4435+11.5         |      4492.7      |      N/A       |       81.2       |          79.4          |        N/A        |
|      Guile (guild 3.0.11)     |         8430=8423+6.6          |      8338.1      |     8317.5     |       56.3       |          58.0          |        N/A        |
|           R (R 4.6.1)         |         2503=2477+26.5         |       15.2       |     2514.6     |        7.0       |          54.7          |        N/A        |

---

### ⚠️ Scope & Methodology Notes

- **What this measures:** Raw front-end symbol ingestion, AST
  traversal, and unoptimized code-generation scaling under a massive,
  single translation unit consisting of synthetic arithmetic call
  chains. The most critical metric for developer productivity is the
  **feedback loop duration**—the combined duration required for a fast
  incremental (semantic) check ("Check"), rebuild, and rerun of unit
  tests ("Total=Build+Run"). In the tables above, the rebuild and rerun
  time is stored in the column titled "Total=Build+Run".
- **Architectural tradeoffs:** Compilers with single-pass
  architectures (e.g., `tcc`) or minimal semantic models will
  naturally outperform multi-pass optimizing compilers (e.g., `rustc`,
  `ghc`, `swiftc`) that perform trait resolution, lifetime/borrow
  validation, or multi-stage IR lowering.
- **Synthetic vs. Real-world:** Real-world build times are heavily
  driven by header parsing (`#include`), package/module resolution,
  standard library footprint, and cross-crate/module parallelism, none
  of which are exercised by isolated arithmetic trees.

## Requirements

- Linux (tested on Arch Linux). CPU pinning uses `os.sched_setaffinity`; other POSIX systems may work with reduced functionality.
- Python 3.12 or later (the script uses `typing.override`).
- [`psutil`](https://pypi.org/project/psutil/) (installed automatically with `pip` on first run if missing).
- Helper modules `process_timer` (providing `ProcessTimer` for RSS sampling) and `cpu_topology` (providing `get_available_cpus` for topology detection) located next to the `benchmark` script.
- At least one of the supported compilers in `PATH` (or in the directory given via `--path`). A subset of them can be installed via `./provision.sh`.

## Supported Languages and Compilers

The *Tier* column controls which result table a compiler ends up in
(see [Understanding Metrics and Table
Output](#understanding-metrics-and-table-output)).

### Native Ahead-of-Time (AOT) Compilers (Tiers 1 & 2)

| Language | Compilers & Toolchains | Operations | Templated | Tier |
| :--- | :--- | :--- | :---: | :---: |
| [Ada](https://en.wikipedia.org/wiki/Ada_(programming_language)) | `gnat` | check, build | – | 2 |
| [C](https://en.wikipedia.org/wiki/C_(programming_language)) | `tcc`, `cuik`, `cproc` | check, compile, build | – | 1 |
| [C](https://en.wikipedia.org/wiki/C_(programming_language)) | [`gcc`](https://gcc.gnu.org/), [`clang`](https://clang.llvm.org/) | check, compile, build | – | 2 |
| [C++](https://isocpp.org/) | [`g++`](https://gcc.gnu.org/), [`clang++`](https://clang.llvm.org/) | check, compile, build | ✓ | 2 |
| [C3](https://c3-lang.org/) | [`c3c`](https://github.com/c3lang/c3c) | check, compile, build | ✓ | 2 |
| [D](https://dlang.org/) | [`dmd`](https://dlang.org/download.html), [`ldmd2`](https://github.com/ldc-developers/ldc), [`gdc`](https://gcc.gnu.org/wiki/GDC) | check, compile, build | ✓ | 2 |
| [Fortran](https://gcc.gnu.org/wiki/GFortran) | `gfortran` | check, compile, build | – | 2 |
| [Go](https://golang.org/) | `go`, `gccgo` | check, build | ✓ | 2 |
| [Hare](https://harelang.org/) | `hare` | check, build | – | 2 |
| [Hylo](https://www.hylo-lang.org/) | `hc` | check, build | ✓ | 2 |
| [Nim](https://nim-lang.org/) | `nim` | check, build | ✓ | 2 |
| [Odin](https://odin-lang.org/) | `odin` | check, build | ✓ | 2 |
| [Pareas](https://github.com/Snektron/pareas) | `pareas` | check, build | – | 2 |
| [Pascal](https://www.freepascal.org/) | `fpc` | check, compile, build | – | 2 |
| [Pony](https://www.ponylang.io/) | `ponyc` | check, build | – | 2 |
| [Roc](https://www.roc-lang.org/) | `roc` | check, build, run | – | 2 |
| [Rust](https://www.rust-lang.org/) | `rustc` | check, build | ✓ | 2 |
| [Swift](https://swift.org/) | `swiftc` | check, build | ✓ | 2 |
| [V](https://vlang.io/) | `v` | check, build | ✓ | 2 |
| [Zig](https://ziglang.org/) | `zig` | ast-check, check, compile, build | ✓ | 2 |

### Managed, VM, JIT & Other Language Toolchains (Tier 3)

| Language | Compilers & Toolchains | Operations | Templated | Tier |
| :--- | :--- | :--- | :---: | :---: |
| [C#](https://learn.microsoft.com/dotnet/csharp/) | `mcs`, `csc` | check, build | – | 3 |
| [Clojure](https://clojure.org/) | `clojure` | check, run | – | 3 |
| [Common-Lisp](https://lisp-lang.org/) | `sbcl` | check, compile, build | – | 3 |
| [Crystal](https://crystal-lang.org/) | `crystal` | check, build | ✓ | 3 |
| [Dart](https://dart.dev/) | `dart` | check, compile, build | ✓ | 3 |
| [Emacs-Lisp](https://gnu.support/gnu-emacs/emacs-lisp/index.html) | `emacs` | check, compile, build | – | 3 |
| [F#](https://fsharp.org/) | `dotnet` | check, run | – | 3 |
| [Guile](https://www.gnu.org/software/guile/) | `guild` | check, compile, build | – | 3 |
| [Haskell](https://www.haskell.org/) | `ghc` | check, build | ✓ | 3 |
| [Java](https://www.oracle.com/java/) | `javac` | check, build | – | 3 |
| [Julia](https://julialang.org/) | `julia` | check, build | ✓ | 3 |
| [Kotlin](https://kotlinlang.org/) | `kotlinc`, `kotlin` | check, run | – | 3 |
| [Lua](https://luajit.org/) | `luajit` | check, compile, build | – | 3 |
| [OCaml](https://ocaml.org/) | `ocamlc`, `ocamlopt` | check, build | – | 3 |
| [Python](https://www.python.org/) | `python3`, `pypy3` | check, compile, build | ✓ | 3 |
| [Scheme](https://cisco.github.io/ChezScheme/) | `chez`, `scheme` | check, compile, build | – | 3 |
| [TypeScript](https://www.typescriptlang.org/) | `tsc` | check, compile, build | ✓ | 3 |
| [R](https://www.r-project.org/) | `R` | check, compile, build | ✓ | 3 |

### Compiler Discovery

- Executables are looked up with `which` in `PATH`, or in the
  directory given by `--path`.
- For compilers that ship with versioned names (`gcc`, `g++`, `clang`,
  `clang++`, `gfortran`, `gnat`, `gccgo`), the unversioned binary as
  well as `-5` to `-19` suffixed binaries (e.g. `gcc-15`) are
  discovered and benchmarked as separate rows.
- Language names given to `--languages` are case-insensitive and
  aliases are accepted (e.g. `ts`/`tsc` for TypeScript, `fpc` for
  Pascal, `ghc` for Haskell, `gfortran` for Fortran, `guild` for
  Guile, `luajit` for Lua, `chez` for Scheme, and
  `lisp`/`sbcl`/`commonlisp` for Common-Lisp).
- When `rustup` is available, Rust is benchmarked on both the `stable`
  and `nightly` channels. Note that this switches your `rustup`
  default toolchain while the benchmark runs.
- Compiler versions are probed automatically (e.g. `--version`, `-v`,
  `version`) and shown in the table's first column.

---

## Benchmark Operations

The benchmark supports up to five distinct operations per compiler target:

| Operation | CLI Flag | Description |
| :--- | :--- | :--- |
| **AST Check** | `ast-check` | Syntax / AST validation only (currently `zig ast-check`). Not part of default operations; enable with `--ast-check` or `--ops=ast-check,...`. |
| **Check** | `check` | Semantic validation and type checking without machine code emission (e.g. `-fsyntax-only`, `--emit=metadata`, `-typecheck`, `--no-codegen`). |
| **Compile** | `compile` | Compiles to object code or bytecode without linking (e.g. `-c`, `py_compile`, or `compile-only`). |
| **Build** | `build` | Full end-to-end compilation and linking producing an executable binary (or bytecode/script artifact for VM languages). |
| **Run** | `run` | Measures execution time of the built artifact over `--run-count` runs. Not a standalone task: the run is performed automatically right after each successful `build`. |

The default operations are `check`, `compile`, `build` and `run`. An operation is only executed for languages that support it (see [Supported Languages and Compilers](#supported-languages-and-compilers)); unsupported combinations are skipped.

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
| `--languages` | `--langs` | All supported (found in `PATH`) | Comma-separated list of languages and optional compilers (`<Lang>:<exe>`). Unknown languages and missing compiler binaries are reported with a warning. |
| `--operations` | `--ops` | `check,compile,build,run` | Comma-separated operations (`ast-check`, `check`, `compile`, `build`, `run`). |
| `--ast-check` | | `false` | Also run AST syntax check (e.g. `zig ast-check`) in addition to selected operations. |
| `--function-count` | `--fc` | `200` | Number of top-level function call chains generated. |
| `--function-depth` | `--fd` | `200` | Nesting call depth per chain (total functions = `fc * fd`). |
| `--run-count` | `--rc` | `10` | Repetitions per compilation step (minimum time recorded). |
| `--timeout` | | `60.0` | Per-compilation timeout in seconds. |
| `--sample-rate` | `--sr` | `100` | Memory sampling frequency (samples/sec) for peak RSS tracking. |
| `--values` | `--val` | `absolute` | Display mode: `absolute`, `relative` (normalized to best), or `both`. |
| `--relative` | `--rel` | `false` | Shortcut for `--values=relative`. |
| `--highlight-min` | `--hl` | `false` | Highlights the lowest (best) metric in each column with HTML badges (applies in every `--values` mode). |
| `--path` | | `None` | Custom search path for locating compiler binaries. |
| `--sort` | `--sort-by` | `total` | Column to sort table results by (`total`, `name`, `lang`, `check`, `compile`, `build`, `run`, `check-rss`, `build-rss`, `output-size`, `size`). Total = Build + Run. |
| `--sort-reverse` | `--sort-desc` | `false` | Sort table results in descending order instead of ascending. |
| `--verbose` | `-v` | `false` | Verbose logging (source generation and per-operation timings). |
| `--progress` | `--progress-format` | `auto` | Progress display: `auto` (tree on capable terminals, line otherwise, none when not a TTY), `tree`, `line`, or `none`. |
| `--print-code` | `--print-generated-code`, `--show-code`, `--pc` | `false` | Print the resulting generated code (sets defaults `--fc=2`, `--fd=2`, `--rc=1`). |

### Parallel Execution Architecture

`benchmark` automatically scales across the available CPU cores:
- Distributes individual benchmark tasks (one per language, operation,
  templated variant and compiler runner) into a
  `multiprocessing.Pool`.
- Detects hybrid CPUs (Intel P/E cores via PMU topology, ARM
  big.LITTLE via `cpu_capacity`, per-core maximum frequency, and Apple
  Silicon performance levels) and, if found, uses **only the
  performance cores**, one worker per core. On homogeneous CPUs it
  uses all available cores minus two (at least one) to leave headroom
  for the system.
- Pins each worker process to a dedicated CPU core via
  `os.sched_setaffinity` to avoid core-hopping noise.
- **Adaptive run count scaling**: When individual compilation
  durations exceed 1.0s, repetitions are capped to 3; when exceeding
  3.0s, repetitions are capped to 2, preventing excessive total
  runtimes while recording accurate minimum timings.
- Generates sources in a temporary root directory (`/tmp/generated_*`)
  and isolates compiler scratchpads in per-process directories
  (`proc_<PID>/<lang>/`).
- Removes a task's scratch directory when it succeeded; if a compiler
  printed output or returned a non-zero exit code, the directory is
  kept for inspection and a warning with the command line, stdout and
  stderr is printed.
- Cleans up temporary files and empty directories upon benchmark
  completion or exit (including `Ctrl-C`).
- Shows live progress (tree or single line) with currently active
  tasks and elapsed times, unless disabled with `--progress=none` or
  when output is not a terminal.

---

## Understanding Metrics and Table Output

Results are printed as Markdown tables, split into three tiers according to compiler architecture:

| Tier | Contents |
| :--- | :--- |
| **Tier 1: Single-Pass / Minimalist Compilers** | `tcc`, `cuik`, `cproc`: no SSA optimization, no borrow checking, trivial type systems, instant code emission. |
| **Tier 2: Modern Systems Languages (Ahead-of-Time)** | Full type inference, monomorphization/generics, semantic safety, module systems. |
| **Tier 3: Managed & VM / JIT / Scripting** | Bytecode emission, runtime metadata, GC runtimes. |

Rows within a tier are sorted by **Total=Build+Run** duration in ascending order. Relative values and highlighting are computed per tier table.

All metric columns in the output Markdown table are normalized per generated function:

$$\text{Total Functions} = \text{function\_count} \times \text{function\_depth}$$

For languages with a safety cap (see below) the capped sizes are used for normalization.

- **`Total=Build+Run [µs/f]`**: Minimum build time plus minimum run
  time per function, shown as `total=build+run`
  (e.g. `105=105+0.20`). Shows `N/A` for toolchains that have no build
  step or whose artifact is not executed.
- **`Check [µs/f]`**, **`Compile [µs/f]`**: Minimum execution duration
  divided by total functions (`args.function_count *
  args.function_depth`). If AST checking is enabled and supported
  (e.g. Zig), its result is appended on a new line (`<br>`) inside the
  **Check** cell.
- **`Check RSS [kB/f]`**, **`Build RSS [kB/f]`**: Maximum resident set
  size (sampled at `--sample-rate` via `psutil` / process timer) in
  kilobytes divided by total functions. Cells show `sampling error` or
  `missing` when memory could not be sampled.
- **`Output Size [B/f]`**: Native binary disk footprint in bytes
  divided by total functions (machine-code binaries only: ELF, Mach-O
  or PE; `N/A` for bytecode/script artifacts).

The time unit of the Check, Compile and Total columns is chosen
automatically per column (`s/f`, `ms/f`, `µs/f` or `ns/f`, based on
the median value) and shown in the column header. In
`--values=relative` mode the header unit is replaced by `[x]`; in
`--values=both` mode each cell shows `absolute (relative)`.

### Stacked Plain and Templated Results

Rather than displaying separate rows, plain and templated/generic results are stacked vertically inside each metric cell using `<br>`:

$$\frac{\langle\text{plain}\rangle}{\langle\text{templated}\rangle}$$

- Non-generic languages display a single value per metric.
- For generic languages, the top row is untemplated and the bottom row
  is templated. A dash `-` indicates that a specific variant was
  unavailable or not evaluated.
- `N/A` is shown when neither variant produced a value
  (e.g. unsupported operation or compilation failure).
- When `--highlight-min` is active, the best plain value and best
  templated value are highlighted independently within their
  respective cell halves.

---

## Generics & Synthetic Code Structure

For languages supporting generics, the benchmark emits an un-templated
test file `main_<run>.<ext>` and a templated test file
`main_t_<run>.<ext>` (one file per repetition). In the templated file,
all functions (except `main`) are generic and instantiated for the
language's 64-bit scalar type. A few languages need different layouts:
Ada uses `main.adb`/`main_t.adb` (the file name must match the unit)
and Pony places every generated program in its own package
subdirectory.

### Semantic Checking Differences

GCC and Clang don't perform all semantic checks for C++ (because it's
too costly). This is in contrast to D's and Rust's compilers that
perform all of them.

### Sample Generated Code (`C`, 3 functions, depth 2)

Running:

```bash
./benchmark --languages=C:tcc --fc=3 --fd=2 --run-count=1 --pc
```

outputs

```c
long add_long_n0_h0(long x) { return x + 79992; }
long add_long_n0(long x) { return x + add_long_n0_h0(x) + 67146; }

long add_long_n1_h0(long x) { return x + 79783; }
long add_long_n1(long x) { return x + add_long_n1_h0(x) + 14363; }

long add_long_n2_h0(long x) { return x + 27403; }
long add_long_n2(long x) { return x + add_long_n2_h0(x) + 13520; }


int main(void) {
    long long_sum = 0;
    long_sum += add_long_n0(0);
    long_sum += add_long_n1(1);
    long_sum += add_long_n2(2);
    return long_sum;
}
```

### Compiler Object Caches

The numerical constants are randomized using a new seed upon every
run. This makes it impossible for compilers to utilize build-caching
mechanisms across successive calls. The purpose of this is to make the
comparison between compilers with and without (different levels of)
caching more fair.

The caching of the Go reference compiler `go`, for instance, is
effectively bypassed by this randomization. The Hare cache directory
(`HARECACHE`) is additionally wiped before each Hare benchmark step.

---

## Compiler Constraints and Safety Caps

Because synthetic code generators create tens of thousands of deeply
nested symbols, compilers encounter internal capacity or scaling
limits. The benchmark automatically enforces stability caps on
affected languages (unaffected languages run at full requested
size). A warning is logged to `stderr` whenever a cap is applied.

---

## Adding a Language

Adding a language only requires inserting one contiguous block into the *LANGUAGE BLOCKS* section of `benchmark`; nothing else needs to change. A block consists of:

1. one or more `bm_<Lang>` runner functions that invoke the
   compiler(s) via `benchmark_compiler_op`, and
2. a single `register_language(LangSupport(...))` call describing
   everything else: compiler executables, file extension, 64-bit
   integer type, supported operations and templated variants, version
   probing (`VersionSpec`), reporting tier, `--languages` aliases,
   argument limits, and all source-code generation hooks (prefix,
   function emitter, `main` header, variable declarations, calls,
   postfix) plus optional quirks (custom program directory, source
   file name, section ordering, or compiler command line).

The generic engine only talks to languages through `LangSupport`.

---

## References

- [Go compilation times compared to C++, D, Rust, Pascal (cross-posted)](https://www.reddit.com/r/golang/comments/55k7n4/go_compilation_times_compared_to_c_d_rust_pascal/)
- [LanguageCompilationSpeed](https://wiki.alopex.li/LanguageCompilationSpeed)
