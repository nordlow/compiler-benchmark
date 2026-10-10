# compiler-benchmark

Benchmarking compilation throughput, peak memory (RSS), and binary
density across 30+ compilers on massive arithmetic translation units.

---

### ⚡ Highlights & Key Findings (AMD Ryzen AI 7 350)

* **DMD's Custom Backend Outperforms by 6×–38×:** Digital Mars D
  (`dmd`) achieves **13 µs/function** (full semantic check + native
  codegen + linking), outperforming minimalist C compilers like `cuik`
  and `cproc`. LLVM-based D (`ldmd2`) is ~6× slower, and GCC-based D
  (`gdc`) is ~38× slower, isolating backend cost.
* **TCC Leads Single-Pass C:** The Tiny C Compiler (`tcc`) streams
  machine code at **4 µs/f**, remaining the undisputed speed champion
  for raw C ingestion.
* **Modern Systems Throughput:** `odin` (147 µs/f) and `zig` (110
  µs/f) stay neck-and-neck with `clang` (118 µs/f), while `rustc` (187
  µs/f) significantly outpaces GCC-based C/C++ (~450–486 µs/f).
* **The Monomorphization Penalty:** Zig demonstrates near-zero generic
  overhead (`comptime` uniform scalars), while Swift’s constraint
  solver balloons build times by 82% (1,239 → 2,258 µs/f) under deep
  call nesting.
* **Untyped vs. Typed Speed:** LuaJIT emits bytecode in 5 µs/f, but
  performs zero compile-time type verification or linking—making DMD's
  fully-typed, native-linked 13 µs/f an extraordinary engineering
  contrast.

---

## AMD Ryzen AI 7 350 (8+8) @ 5.09 GHz

The output on Arch Linux (as of 2026-09) for the sample call
`./benchmark` results in the following tables:

### Modern Systems Languages (Ahead-of-Time)
*Full type inference, monomorphization/generics, semantic safety, module systems.*

*Stacked cells: top = untemplated, bottom = templated (`-` = not available).*

|          Language (Exec)          |      Total=Build+Run [us/f]     |   Check [us/f]  | Compile [us/f] | Check RSS [kB/f] | Build RSS [kB/f] | Output Size [B/f] |
| :-------------------------------: | :-----------------------------: | :-------------: | :------------: | :--------------: | :--------------: | :---------------: |
|      D (dmd 2.113.0-95551bb)      |     13=13+0.20<br>19=19+0.04    |   4.5<br>15.8   |  10.3<br>17.9  |   4.8<br>12.0    |   15.3<br>24.0   |   178.5<br>194.5  |
|          D (ldmd2 1.43.0)         |     95=94+0.19<br>84=84+0.04    |   5.8<br>23.6   |  73.7<br>92.5  |   7.8<br>14.9    |   15.8<br>32.3   |   168.9<br>163.0  |
| Zig (zig 0.18.0-dev.35+5e754304d) |    110=109+0.20<br>92=92+0.21   |   22.3<br>33.8  | 93.2<br>109.8  |    4.5<br>5.2    |   8.6<br>12.7    |  1503.4<br>1422.5 |
|          C (clang 23.1.1)         |           118=117+1.2           |       13.5      |      77.9      |       3.3        |       6.8        |       146.1       |
|         Pascal (fpc 3.2.2)        |           138=137+0.20          |       98.7      |     103.6      |       17.9       |       24.6       |        68.8       |
| Odin (odin dev-2026-09:a2fb372b7) |    147=147+0.20<br>98=98+0.10   |   19.1<br>47.0  |      N/A       |   20.5<br>31.0   |   34.0<br>51.8   |   112.6<br>132.6  |
|        Hare (hare 0.26.0.1)       |           150=150+0.05          |      135.9      |      N/A       |      110.8       |      110.8       |       222.0       |
|           C3 (c3c 0.8.5)          |   153=152+0.21<br>255=254+0.20  |   15.0<br>94.9  | 109.3<br>256.6 |    6.2<br>7.7    |   15.5<br>23.6   |   338.8<br>418.5  |
|    Rust (rustc 1.100.0-nightly)   |   187=187+0.21<br>238=238+0.19  |  86.3<br>141.5  |      N/A       |   16.2<br>15.2   |   32.0<br>26.4   |   360.4<br>300.3  |
|        C++ (clang++ 23.1.1)       |   236=236+0.21<br>107=107+0.10  |   17.2<br>27.8  | 82.4<br>128.7  |    3.6<br>6.1    |   7.6<br>13.0    |   151.1<br>142.2  |
|        C++ (g++-15 15.3.0)        |   303=303+0.20<br>600=600+0.09  |   27.1<br>67.2  | 269.6<br>665.0 |   7.0<br>10.7    |   17.5<br>23.3   |   126.1<br>127.2  |
|         C (gcc-15 15.3.0)         |           392=392+0.10          |       11.9      |     193.8      |       3.7        |       17.2       |       121.1       |
|         Roc (roc compiler)        |          396=237+158.7          |       89.9      |      N/A       |       33.0       |       44.3       |       431.4       |
|     Go (go 1.27.1-X:nodwarf5)     |   418=418+0.09<br>453=453+0.09  |   53.3<br>52.3  |      N/A       |   10.7<br>10.4   |   30.9<br>30.7   |   188.9<br>188.9  |
|            V (v 0.5.0)            |      444=444+0.20<br>>60.0s     |  10.1<br>899.0  |      N/A       |  10.2<br>181.4   |  36.1<br>198.8   |     132.3<br>-    |
|           C (gcc 16.2.1)          |           454=454+0.21          |       11.8      |     400.1      |       3.9        |       17.6       |       121.1       |
|          C++ (g++ 16.2.1)         |   486=486+0.21<br>566=566+0.10  |   33.1<br>84.3  | 372.3<br>524.8 |   7.6<br>11.1    |   17.4<br>23.7   |   126.1<br>127.2  |
|           D (gdc 16.2.1)          |   527=527+0.21<br>444=444+0.09  |   15.9<br>31.3  | 497.1<br>515.8 |   6.5<br>15.9    |   23.4<br>33.8   |   178.3<br>182.4  |
|          Nim (nim 2.2.12)         |   675=675+0.21<br>652=652+0.19  |  84.5<br>146.6  |      N/A       |   7.5<br>14.9    |   43.8<br>49.6   |   178.0<br>181.4  |
|    Pony (ponyc 0.72.1-de5eddd)    |           963=963+0.0           |      390.4      |      N/A       |      197.7       |      282.2       |       804.8       |
|         Ada (gnat 16.2.1)         |          1124=1124+0.38         |       34.7      |      N/A       |       19.8       |       51.7       |       263.0       |
|     Fortran (gfortran 16.2.1)     |          1147=1147+0.18         |      527.1      |     962.6      |       22.0       |       37.2       |       140.8       |
|         Swift (swiftc 6.4)        | 1239=1237+1.6<br>2258=2258+0.83 | 661.3<br>1265.9 |      N/A       |   33.5<br>28.9   |   45.6<br>68.7   |   208.5<br>531.3  |
|          Vox (vox master)         |               N/A               |       N/A       |      N/A       |    0.7<br>0.6    |    0.5<br>0.5    |        N/A        |

### Single-Pass / Minimalist Compilers
*No SSA optimization, no borrow checking, trivial type systems, instant code emission.*

| Language (Exec)  | Total=Build+Run [us/f] | Check [us/f] | Compile [us/f] | Check RSS [kB/f] | Build RSS [kB/f] | Output Size [B/f] |
| :--------------: | :--------------------: | :----------: | :------------: | :--------------: | :--------------: | :---------------: |
| C (tcc 0.9.28rc) |        4=4+0.21        |     2.4      |      2.0       |       1.1        |       0.8        |        90.1       |
| C (cuik ~master) |       76=75+0.42       |     3.9      |      38.7      |       3.2        |       51.6       |       114.4       |
|    C (cproc)     |       86=86+0.21       |     9.4      |      73.9      |       2.4        |       2.7        |        90.1       |

### Managed & VM / JIT / Scripting
*Bytecode emission, runtime metadata, GC runtimes.*

*Stacked cells: top = untemplated, bottom = templated (`-` = not available).*

|        Language (Exec)        |     Total=Build+Run [us/f]     |   Check [us/f]   | Compile [us/f] | Check RSS [kB/f] | Build RSS [kB/f] | Output Size [B/f] |
| :---------------------------: | :----------------------------: | :--------------: | :------------: | :--------------: | :--------------: | :---------------: |
|  Lua (luajit 2.1.1788856981)  |            5=3+1.4             |       3.8        |      3.3       |       0.8        |       0.7        |        N/A        |
|    Python (python3 3.14.7)    |     35=32+2.9<br>48=42+5.4     |   29.5<br>37.1   |  30.0<br>41.7  |   11.2<br>14.3   |   11.3<br>14.3   |        N/A        |
| Python (python3.15 3.15.0rc3) |     37=34+2.9<br>56=49+6.6     |   38.7<br>50.1   |  39.6<br>53.0  |   11.3<br>14.3   |   11.3<br>14.5   |        N/A        |
|       C# (mcs 6.12.0.0)       |           53=37+16.6           |       34.0       |      N/A       |       5.1        |       5.2        |        N/A        |
|     Python (pypy3 3.12.14)    |     64=55+9.1<br>66=56+9.1     |   48.3<br>58.0   |  56.0<br>61.0  |   11.1<br>12.3   |   13.0<br>13.7   |        N/A        |
|      OCaml (ocamlc 5.5.0)     |          143=143+0.05          |      124.0       |      N/A       |       16.7       |       20.4       |        N/A        |
|   C# (csc 3.9.0-6.21124.20)   |          205=195+9.1           |       46.7       |      N/A       |       7.6        |       10.1       |        N/A        |
|      Scheme (chez 10.3.0)     |          268=251+16.6          |       8.9        |     247.1      |       1.4        |       12.0       |        N/A        |
|       Dart (dart 3.13.5)      |  292=291+0.41<br>436=435+0.41  |  204.6<br>253.6  | 317.6<br>408.9 |   13.0<br>15.7   |   10.4<br>11.0   |   430.6<br>500.3  |
|    Crystal (crystal 1.21.1)   |  391=390+0.41<br>369=368+0.40  |  145.6<br>128.2  |      N/A       |   33.0<br>31.1   |   83.4<br>81.6   |   384.9<br>384.9  |
|        Java (javac 27)        |          431=419+11.5          |      174.9       |      N/A       |       17.9       |       26.8       |        N/A        |
|     TypeScript (tsc 6.0.3)    |  464=453+11.5<br>492=481+11.5  |  375.0<br>439.0  | 464.3<br>458.4 |   40.2<br>40.7   |   40.0<br>42.5   |        N/A        |
|    Julia (julia 1.14.0-DEV)   |   510=510+0.0<br>439=439+0.0   |   17.5<br>14.2   |      N/A       |    8.8<br>8.4    |   12.8<br>12.3   |        N/A        |
|     OCaml (ocamlopt 5.5.0)    |          522=521+0.21          |      118.4       |      N/A       |       16.8       |       52.2       |       579.1       |
|    Common Lisp (sbcl 2.6.9)   |          570=569+0.41          |      482.9       |     497.0      |       4.2        |       5.7        |       1481.3      |
|      Haskell (ghc 9.6.7)      | 3966=3965+1.6<br>4115=4114+1.6 | 2344.2<br>2435.8 |      N/A       |   62.6<br>63.3   |   82.2<br>84.8   |   657.3<br>616.3  |
|      Guile (guild 3.0.11)     |         8354=8347+6.6          |      8662.4      |     8130.0     |       48.3       |       49.6       |        N/A        |

## Conclusions (from sample run shown above)

### 1. Front-End Architecture & Ingestion Speed
* **Single-pass dominance (`tcc`)**: The Tiny C Compiler (`tcc`) is the fastest native machine-code compiler overall by a wide margin (2 µs/f total build time, 1.1 kB/f peak RSS). Its single-pass architecture avoids constructing a full multi-pass AST or SSA intermediate representation, streaming machine code directly as symbols are ingested.
* **Custom backends vs. heavy optimizing backends (`dmd` vs. `ldmd2` / `gcc`)**:
  * Among modern systems languages (Tier 2), Digital Mars D (`dmd`) is exceptionally fast (9–13 µs/f plain, 12–19 µs/f templated)—outperforming not only all Tier 2 languages, but also minimalist C compilers like `cuik` (47 µs/f) and `cproc` (78 µs/f).
  * Comparing D compilers isolates backend overhead: the custom DMD backend compiles in 11.5 µs/f, whereas LLVM-based LDC (`ldmd2`) requires 70.3 µs/f (~6× slower) and GCC-based GDC (`gdc`) takes 433.2 µs/f (~38× slower).
* **Modern systems language throughput**: `odin` (92 µs/f) and `zig` (97 µs/f) achieve compilation speeds on par with or faster than `clang` (87 µs/f), while `rustc` (183 µs/f) handily outperforms both GCC-based C/C++ front-ends (~418–455 µs/f).

### 2. Generics & Monomorphization Overhead
* **Zero-cost monomorphization**: `zig` demonstrated effectively identical compile speeds between untemplated and templated code (97 µs/f vs. 92 µs/f), reflecting the efficiency of its `comptime` evaluation for uniform scalar types.
* **Moderate generic penalties**: `dmd` (+46%), `rustc` (+30%), and `c3c` (+77%) exhibit predictable, linear increases in build time when resolving and instantiating generic arithmetic functions.
* **Solver and inference blowups**:
  * **Swift (`swiftc`)**: Suffers a ~2× slowdown on templated code (1174 µs/f → 2287 µs/f), driven primarily by type checker and constraint-solver overhead during deep function call validation (check time ballooned from 728.6 to 1319.7 µs/f).
  * **V (`v`)**: While plain compilation completed in 317 µs/f, templated compilation timed out (>60.0s) and check memory exploded from 10.2 kB/f to 181.5 kB/f.

### 3. Compiler Version Regressions
* Newer compiler releases can introduce regressions in raw front-end ingestion. Between **GCC 15.3.0** and **GCC 16.2.1**:
  * Unlinked C compilation (`compile`) regressed from 226.7 µs/f to 382.6 µs/f (+68.8%).
  * C++ compilation (`g++`) regressed from 209.4 µs/f to 422.2 µs/f (+101.6%—more than double the time).

### 4. Memory Footprint (Peak RSS)
* **Leanest**: LuaJIT (`luajit`, 0.7–0.8 kB/f), `tcc` (1.1 kB/f), `cproc` (3.8 kB/f), and `dmd` (16.7 kB/f build / 4.9 kB/f check) maintain minimal memory overhead throughout compilation.
* **Heaviest**: Pony (`ponyc`, 283.3 kB/f), Hare (`hare`, 110.8 kB/f), Haskell (`ghc`, 81.8–88.5 kB/f), and Crystal (`crystal`, 81.7–83.7 kB/f) exhibit the highest peak memory per function, reflecting the memory cost of capability tracking, global analysis, and whole-program AST retention.

### 5. Binary Footprint & Output Density
* **Most compact machine code**: Free Pascal (`fpc`, 68.8 B/f), `tcc` / `cproc` (90.1 B/f), `odin` (112.6 B/f), and `gcc` (121.1 B/f) generate the most compact executables per function.
* **Code bloat & runtime overhead**: `zig` (1422–1503 B/f) and Common Lisp (`sbcl`, 1481 B/f) produce significantly larger binary sizes per function, primarily due to runtime scaffolding, unwinding metadata, and alignment padding.

### 6. Managed, VM, and Scripting Toolchains (Tier 3)
* **Untyped bytecode emission vs. static type safety (The Lua vs. D fallacy)**:
  * While LuaJIT (`luajit`, 4 µs/f build, 4.4 µs/f check) clocks a raw ingestion speed faster than D (`dmd`, 9–13 µs/f), **stating that "Lua compiles faster than D" is fundamentally an apples-to-oranges comparison**:
    * **Zero compile-time type verification**: Lua is completely dynamically typed. Its parser performs no type checking, no signature validation, and no static symbol binding for globals. Global function calls are emitted directly as dynamic string table lookups against `_ENV`, deferring all resolution and type safety checks entirely to runtime.
    * **No native codegen or linking**: LuaJIT emits lightweight virtual machine bytecode chunks in a single pass without building full symbol tables, allocating machine registers, or invoking a system linker.
    * **D's engineering achievement**: In contrast, DMD performs exhaustive static type checking, semantic analysis, attribute verification (`@safe`, `pure`, `nothrow`, `@nogc`), monomorphization, and machine code generation with full native linking. Completing all of this in just ~9–13 µs/f highlights the extraordinary efficiency of DMD's front-end and custom backend relative to what Lua is actually asked to do.
* **Legacy vs. Modern managed toolchains**: In C#, Mono's older C# compiler (`mcs`, 36 µs/f build) compiles ~6× faster than the modern Roslyn compiler (`csc`, 214 µs/f build), illustrating how much semantic analysis modern Roslyn pipelines perform.
* **Functional & CPS transformation costs**: Functional languages performing deep intermediate representations—such as Scheme/Guile's Tree-IL Continuation-Passing Style compiler (`guild`, 8543 µs/f build) and Haskell (`ghc`, 3894–4704 µs/f build)—face steep scaling penalties on deep, non-inlined synthetic call trees.

### 7. Scalability Bottlenecks & Caps
Synthetic call chains stress corner cases that standard module-based codebases rarely trigger, explaining why automatic caps are required:
* **Table and pool overflows**: Java caps at $100 \times 100$ due to the JVM 16-bit constant pool ceiling ($65{,}535$ entries); LuaJIT caps at $150 \times 150$ due to the bytecode chunk constant limit ($65{,}536$).
* **Recursion & elaboration limits**: Nim enforces an internal compiler limit of 50 recursive generic instantiations (forcing `--function-depth` to 50); Ada requires capping at $100 \times 100$ due to quadratic scaling in `gnatbind` elaboration analysis.
* **CPS & capability checking**: Pony ($30 \times 30$), Roc ($50 \times 50$), and Guile ($70 \times 70$) hit pathologically slow type/capability checking or CPS lowering times on tens of thousands of deeply nested expressions.

---

### ⚠️ Scope & Methodology Notes

- **What this measures:** Raw front-end symbol ingestion, AST
  traversal, and unoptimized code-generation scaling under a massive,
  single translation unit consisting of synthetic arithmetic call
  chains. The most critical metric for developer productivity is the
  **feedback loop duration**—the combined duration required for a fast
  incremental (semantic) check, rebuild, and rerun of unit tests. In
  the tables below, this is stored in the column titled
  "Total=Build+Run".
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
- [Python](https://www.python.org/) (using `python3`, `pypy3`)
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
| Python | `python3`, `pypy3` | check, compile, build | ✓ | 3 |
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
- Language names given to `--languages` are case-insensitive and aliases are accepted (e.g. `ts`/`tsc` for TypeScript, `fpc` for Pascal, `ghc` for Haskell, `gfortran` for Fortran, `guild` for Guile, `luajit` for Lua, `chez` for Scheme, and `lisp`/`sbcl`/`commonlisp` for Common Lisp).
- When `rustup` is available, Rust is benchmarked on both the `stable` and `nightly` channels. Note that this switches your `rustup` default toolchain while the benchmark runs.
- Compiler versions are probed automatically (e.g. `--version`, `-v`, `version`) and shown in the table's first column.

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

The default operations are `check`, `compile`, `build` and `run`. An operation is only executed for languages that support it (see the [Support Matrix](#support-matrix)); unsupported combinations are skipped.

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
| `--verbose` | `-v` | `false` | Verbose logging (source generation and per-operation timings). |
| `--progress` | `--progress-format` | `auto` | Progress display: `auto` (tree on capable terminals, line otherwise, none when not a TTY), `tree`, `line`, or `none`. |

### Parallel Execution Architecture

`benchmark` automatically scales across the available CPU cores:
- Distributes individual benchmark tasks (one per language, operation, templated variant and compiler runner) into a `multiprocessing.Pool`.
- Detects hybrid CPUs (Intel P/E cores via PMU topology, ARM big.LITTLE via `cpu_capacity`, per-core maximum frequency, and Apple Silicon performance levels) and, if found, uses **only the performance cores**, one worker per core. On homogeneous CPUs it uses all available cores minus two (at least one) to leave headroom for the system.
- Pins each worker process to a dedicated CPU core via `os.sched_setaffinity` to avoid core-hopping noise.
- **Adaptive run count scaling**: When individual compilation durations exceed 1.0s, repetitions are capped to 3; when exceeding 3.0s, repetitions are capped to 2, preventing excessive total runtimes while recording accurate minimum timings.
- Generates sources in a temporary root directory (`/tmp/generated_*`) and isolates compiler scratchpads in per-process directories (`proc_<PID>/<lang>/`).
- Removes a task's scratch directory when it succeeded; if a compiler printed output or returned a non-zero exit code, the directory is kept for inspection and a warning with the command line, stdout and stderr is printed.
- Cleans up temporary files and empty directories upon benchmark completion or exit (including `Ctrl-C`).
- Shows live progress (tree or single line) with currently active tasks and elapsed times, unless disabled with `--progress=none` or when output is not a terminal.

---

## Understanding Metrics and Table Output

Results are printed as Markdown tables, split into three tiers according to compiler architecture:

| Tier | Contents |
| :--- | :--- |
| **Tier 1: Single-Pass / Minimalist Compilers** | `tcc`, `cuik`, `cproc`: no SSA optimization, no borrow checking, trivial type systems, instant code emission. |
| **Tier 2: Modern Systems Languages (Ahead-of-Time)** | Full type inference, monomorphization/generics, semantic safety, module systems. |
| **Tier 3: Managed & VM / JIT / Scripting** | Bytecode emission, runtime metadata, GC runtimes. |

Rows within a tier are sorted alphabetically. Relative values and highlighting are computed per tier table.

All metric columns in the output Markdown table are normalized per generated function:

$$\text{Total Functions} = \text{function\_count} \times \text{function\_depth}$$

For languages with a safety cap (see below) the capped sizes are used for normalization.

- **`Total=Build+Run [us/f]`**: Minimum build time plus minimum run time per function, shown as `total=build+run` (e.g. `105=105+0.20`). Shows `N/A` for toolchains that have no build step or whose artifact is not executed.
- **`Check [us/f]`**, **`Compile [us/f]`**: Minimum execution duration divided by total functions (`args.function_count * args.function_depth`). If AST checking is enabled and supported (e.g. Zig), its result is appended on a new line (`<br>`) inside the **Check** cell.
- **`Check RSS [kB/f]`**, **`Build RSS [kB/f]`**: Maximum resident set size (sampled at `--sample-rate` via `psutil` / process timer) in kilobytes divided by total functions. Cells show `sampling error` or `missing` when memory could not be sampled.
- **`Output Size [B/f]`**: Native binary disk footprint in bytes divided by total functions (machine-code binaries only: ELF, Mach-O or PE; `N/A` for bytecode/script artifacts).

The time unit of the Check, Compile and Total columns is chosen automatically per column (`s/f`, `ms/f`, `us/f` or `ns/f`, based on the median value) and shown in the column header. In `--values=relative` mode the header unit is replaced by `[x]`; in `--values=both` mode each cell shows `absolute (relative)`.

### Stacked Plain and Templated Results

Rather than displaying separate rows, plain and templated/generic results are stacked vertically inside each metric cell using `<br>`:

$$\frac{\langle\text{plain}\rangle}{\langle\text{templated}\rangle}$$

- Non-generic languages display a single value per metric.
- For generic languages, the top row is untemplated and the bottom row is templated. A dash `-` indicates that a specific variant was unavailable or not evaluated.
- `N/A` is shown when neither variant produced a value (e.g. unsupported operation or compilation failure).
- When `--highlight-min` is active, the best plain value and best templated value are highlighted independently within their respective cell halves.

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

The numerical constants are randomized using a new seed upon every run. This makes it impossible for compilers to utilize build-caching mechanisms across successive calls. The purpose of this is to make the comparison between compilers with and without (different levels of) caching more fair.

The caching of the Go reference compiler `go`, for instance, is effectively bypassed by this randomization. The Hare cache directory (`HARECACHE`) is additionally wiped before each Hare benchmark step.

---

## Compiler Constraints and Safety Caps

Because synthetic code generators create tens of thousands of deeply nested symbols, compilers encounter internal capacity or scaling limits. The benchmark automatically enforces stability caps on affected languages (unaffected languages run at full requested size):

- **Pony**: Capped to $30 \times 30$ ($900$ functions) due to `ponyc` capability checker limits.
- **Roc**: Capped to $50 \times 50$ ($2{,}500$ functions) due to compiler limits.
- **Guile**: Capped to $70 \times 70$ ($4{,}900$ functions) due to Tree-IL CPS compiler scaling limits.
- **Ada**: Capped to $100 \times 100$ ($10{,}000$ functions) due to quadratic scaling in `gnatbind` elaboration analysis.
- **Swift**: Capped to $100 \times 100$ ($10{,}000$ functions) due to `swiftc` constraint solver limits.
- **Crystal & TypeScript**: Capped to $100 \times 100$ ($10{,}000$ functions) due to global type inference and AST heap limits.
- **Haskell**: Capped to $100 \times 100$ ($10{,}000$ functions) due to GHC scaling limits.
- **Fortran**: Capped to $100 \times 100$ ($10{,}000$ functions) due to `gfortran` module symbol table limits.
- **Java**: Capped to $100 \times 100$ ($10{,}000$ functions) to prevent exceeding the JVM $65{,}535$ constant pool limit per class file.
- **Cuik**: Function count and depth are each capped to $100$ due to compiler stability limits.
- **Lua / LuaJIT**: Capped to $150 \times 150$ ($22{,}500$ functions) to avoid exceeding the LuaJIT bytecode chunk constant limit ($65{,}536$).
- **OCaml & Julia**: Capped to $200 \times 200$ once requested total functions exceed $10{,}000$ due to nested call-tree scaling limits.
- **Nim**: `--function-depth` is automatically truncated to $50$ due to Nim's internal recursion limit on generic instantiations.

A warning is logged to `stderr` whenever a cap is applied.

---

## Adding a Language

Adding a language only requires inserting one contiguous block into the *LANGUAGE BLOCKS* section of `benchmark`; nothing else needs to change. A block consists of:

1. one or more `bm_<Lang>` runner functions that invoke the compiler(s) via `benchmark_compiler_op`, and
2. a single `register_language(LangSupport(...))` call describing everything else: compiler executables, file extension, 64-bit integer type, supported operations and templated variants, version probing (`VersionSpec`), reporting tier, `--languages` aliases, argument limits, and all source-code generation hooks (prefix, function emitter, `main` header, variable declarations, calls, postfix) plus optional quirks (custom program directory, source file name, section ordering, or compiler command line).

The generic engine only talks to languages through `LangSupport`.

---

## References

- [Go compilation times compared to C++, D, Rust, Pascal (cross-posted)](https://www.reddit.com/r/golang/comments/55k7n4/go_compilation_times_compared_to_c_d_rust_pascal/)
- [LanguageCompilationSpeed](https://wiki.alopex.li/LanguageCompilationSpeed)
