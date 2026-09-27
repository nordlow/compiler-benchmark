# compiler-benchmark

Benchmarks compilation speeds, memory consumption (peak RSS), and binary output sizes across different programming languages and compilers.

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
- [Rust](https://www.rust-lang.org/) (using `rustc`)
- [Swift](https://swift.org/) (using `swiftc`)
- [V](https://vlang.io/) (using `v`)
- [Vox](https://github.com/MrSmith33/vox) (using `vox`)
- [Zig](https://ziglang.org/) (using `zig`)
- [Dart](https://dart.dev/) (using `dart`)
- [SBCL](https://www.sbcl.org/) (using `sbcl`)
- [Guile](https://www.gnu.org/software/guile/) (using `guile`)

### Bytecode, VM, and JIT/Scripting Toolchains
- [C#](https://learn.microsoft.com/dotnet/csharp/) (using `csc` or `mcs`, executed via `mono`)
- [Java](https://www.oracle.com/java/) (using `javac`, executed via `java`)
- [Julia](https://julialang.org/) (using `julia`)
- [Lua](https://luajit.org/) (using `luajit`)
- [OCaml Bytecode](https://ocaml.org/) (using `ocamlc`, executed via `ocamlrun`)
- [Python](https://www.python.org/) (using `python3`, `python`, `pypy3`, `pypy`)
- [Scheme](https://cisco.github.io/ChezScheme/) (using `chez`, `scheme`)
- [TypeScript](https://www.typescriptlang.org/) (using `tsc`)

A subset of these compilers can be installed on Linux via `./provision.sh` (tested on Arch Linux).

---

## Benchmark Operations

The benchmark supports up to five distinct operations per compiler target:

| Operation | CLI Flag | Description |
| :--- | :--- | :--- |
| **AST Check** | `ast-check` | Syntax / AST validation only (e.g. `zig ast-check`). |
| **Check** | `check` | Semantic validation and type checking without machine code emission (e.g. `-fsyntax-only`, `cargo check` equivalent `--emit=metadata`, or `-typecheck`). |
| **Compile** | `compile` | Compiles to object code or bytecode without linking (e.g. `-c`, `py_compile`, or `compile-only`). |
| **Build** | `build` | Full end-to-end compilation and linking producing an executable binary. |
| **Run** | `run` | Measures execution time of the built artifact over `--run-count` runs. |

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
./benchmark --fc=200 --fd=200 --rc=5 --ops=check,build,run
```

Filter specific languages or explicit compiler executables:

```bash
./benchmark --languages=C:tcc,C:gcc,C++,D:dmd,D:ldmd2,D:gdc,Rust
```

### CLI Arguments Reference

| Option | Short | Default | Description |
| :--- | :--- | :--- | :--- |
| `--languages` | `--langs` | All supported | Comma-separated list of languages and optional compilers (`<Lang>:<exe>`). |
| `--operations` | `--ops` | All operations | Comma-separated operations (`ast-check`, `check`, `compile`, `build`, `run`). |
| `--function-count` | `--fc` | `200` | Number of top-level function call chains generated. |
| `--function-depth` | `--fd` | `200` | Nesting call depth per chain (total functions = `fc * fd`). |
| `--run-count` | `--rc` | `5` | Repetitions per compilation step (minimum time recorded). |
| `--sample-rate` | `--sr` | `100` | Memory sampling frequency (samples/sec) for peak RSS tracking. |
| `--values` | `--val` | `absolute` | Display mode: `absolute`, `relative` (normalized to best), or `both`. |
| `--relative` | `--rel` | `false` | Shortcut for `--values=relative`. |
| `--highlight-min` | `--hl` | `false` | Highlights the lowest (best) metric in each column with HTML badges. |
| `--path` | | `None` | Custom search path for locating compiler binaries. |

### Parallel Execution Architecture

`benchmark` automatically scales across all available CPU cores:
- Distributes individual benchmark tasks into a `multiprocessing.Pool` sized to the available CPU cores.
- Pins each worker process to a dedicated CPU core via `os.sched_setaffinity` to avoid core-hopping noise.
- Isolates compiler scratchpads into per-process directories (`generated/proc_<PID>/<lang>/`).
- Automatically cleans up temporary files and directories upon benchmark completion or exit.

---

## Understanding Metrics and Table Output

All metric columns in the output Markdown table are normalized per generated function:

$$\text{Total Functions} = \text{function\_count} \times \text{function\_depth}$$

- **`AST-C [us/f]`**, **`Check [us/f]`**, **`Compile [us/f]`**, **`Build [us/f]`**: Minimum execution duration in microseconds divided by total functions (`args.function_count * args.function_depth`).
- **`Run [us/f]`**: Minimum binary execution time in microseconds (or fractional) divided by total functions.
- **`Check RSS [kB/f]`**, **`Build RSS [kB/f]`**: Maximum resident set size (sampled via `psutil` / process timer) in kilobytes divided by total functions.
- **`Output Size [B/f]`**: Stripped binary disk footprint in bytes divided by total functions (native machine-code binaries only).

### Merged Plain and Templated Results

Rather than displaying separate rows, plain and templated/generic results are merged into each metric cell as:

$$\langle\text{plain}\rangle,\langle\text{templated}\rangle$$

- A dash `-` indicates that the corresponding variant does not apply or was not evaluated (e.g. `1897.3,-` for non-generic languages or `-,120.4` for template-only tests).
- When `--highlight-min` is active, the best plain value and best templated value are highlighted independently within their respective cell halves.

---

## Generics & Synthetic Code Structure

For languages supporting generics, the benchmark emits an un-templated test file `main.<ext>` and a templated test file `main_t.<ext>`. In the templated file, all functions (except `main`) are generic and instantiated for the language's 64-bit scalar type.

### Semantic Checking Differences

GCC and Clang don't perform all semantic checks for C++ (because it's too costly). This is in contrast to D's and Rust's compilers that perform all of them.

### Sample Generated Code (`C`, 3 functions, depth 2)

Running:

```bash
./benchmark --function-count=3 --function-depth=2 --run-count=5
```

produces `generated/proc_<PID>/c/main_0.c`:

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

The caching of the Go reference compiler `go`, for instance, is effectively disabled by this randomization.

---

## Compiler Constraints and Safety Caps

Because synthetic code generators create tens of thousands of deeply nested symbols, certain compilers encounter internal limits. The benchmark automatically enforces the following stability caps:

- **Both OCaml and Julia** scale poorly on deeply nested functions with large synthetic function counts, so an explicit maximum limit of $200 \times 200$ is enforced.
- **Nim**: The Nim compiler has a hard limit of 50 recursive generic instantiations, so `--function-depth` is automatically truncated down to `50`.
- **Java**: Capped to $100 \times 100$ ($10{,}000$ functions) to avoid exceeding the JVM $65{,}535$ constant pool entry limit per class file.
- **Lua / LuaJIT**: Capped to $150 \times 150$ to avoid exceeding the LuaJIT bytecode chunk constant table limit ($65{,}536$).
- **Cuik**: Capped to $100 \times 100$ due to compiler stability limits.

---

## AMD Ryzen AI 7 350 (8+8) @ 5.09 GHz

The output on Arch Linux (as of 2026-09) for the sample call

    ./benchmark --function-count=200 --function-depth=200 --run-count=3

results in the following table (copied from the output at the end).

| Lang-uage | AST-C [us/f] | Check [us/f]    | Compile [us/f] | Build [us/f]    | Run [us/f]    | Check RSS [kB/f] | Build RSS [kB/f]      | Output Size [B/f] | Version                         | Exec     |
| :-------: | :----------: | :-------------: | :------------: | :-------------: | :-----------: | :--------------: | :-------------------: | :---------------: | :-----------------------------: | :------: |
| Ada       | N/A          | N/A             | N/A            | 1897.3,-        | 195,-         | N/A              | 39.6,-                | 240.0,-           | 16.2.1                          | gnat     |
| C         | N/A          | 14.3,-          | 83.5,-         | 85.3,-          | 160,-         | 3.4,-            | 10.5,-                | 146.1,-           | 22.1.8                          | clang    |
| C         | N/A          | 9.9,-           | 76.2,-         | N/A             | N/A           | 2.4,-            | 3.8,-                 | N/A               | unknown                         | cproc    |
| C         | N/A          | 4.5,-           | 80.6,-         | 81.6,-          | 202,-         | 3.0,-            | 82.6,-                | 114.4,-           | ~master                         | cuik     |
| C         | N/A          | 17.8,-          | 808.3,-        | 805.8,-         | 125,-         | 4.0,-            | 18.0,-                | 121.1,-           | 16.2.1                          | gcc      |
| C         | N/A          | 17.8,-          | 830.3,-        | 821.7,-         | 363,-         | 3.8,-            | 16.2,-                | 121.1,-           | 15.3.0                          | gcc-15   |
| C         | N/A          | 2.4,-           | 3.3,-          | 3.6,-           | 137,-         | 1.1,-            | 1.1,-                 | 90.1,-            | 0.9.28rc                        | tcc      |
| C#        | N/A          | 76.8,-          | N/A            | 270.6,-         | 10975,-       | 7.6,-            | 10.0,-                | N/A               | 3.9.0-6.21124.20                | csc      |
| C#        | N/A          | 45.0,-          | N/A            | 41.8,-          | 16392,-       | 5.1,-            | 5.0,-                 | N/A               | 6.12.0.0                        | mcs      |
| C++       | N/A          | 17.4,44.0       | 165.1,126.3    | 88.7,148.3      | 188,197       | 3.6,5.9          | 10.4,13.3             | 151.1,155.1       | 22.1.8                          | clang++  |
| C++       | N/A          | 45.8,103.9      | 842.4,527.8    | 543.1,652.7     | 144,173       | 7.7,11.3         | 18.3,21.8             | 126.1,130.1       | 16.2.1                          | g++      |
| C++       | N/A          | 41.6,110.0      | 827.9,559.7    | 508.6,574.8     | 144,233       | 7.0,10.5         | 17.6,21.5             | 126.1,130.1       | 15.3.0                          | g++-15   |
| C3        | N/A          | 25.2,101.5      | 113.1,262.9    | 206.4,294.2     | 187,185       | 6.0,7.5          | 17.7,22.9             | 338.8,418.5       | 0.8.5                           | c3c      |
| Crystal   | N/A          | 97.7,104.8      | N/A            | 291.7,223.7     | 120,117       | 14.7,13.6        | 31.8,32.0             | 271.9,271.9       | 1.21.0                          | crystal  |
| D         | N/A          | 6.0,17.2        | 16.4,26.4      | 21.1,33.1       | 140,66        | 5.0,12.2         | 17.0,24.5             | 178.5,194.5       | v2.113.0-beta.1-954-g93f0bc94c5 | dmd      |
| D         | N/A          | 16.6,49.6       | 653.6,543.3    | 691.7,853.6     | 263,74        | 6.5,15.9         | 24.2,34.0             | 178.3,182.4       | 16.2.1                          | gdc      |
| D         | N/A          | 6.7,22.4        | 103.5,109.2    | 118.8,128.8     | 188,182       | 7.7,17.8         | 20.7,31.9             | 168.9,163.0       | 1.43.0                          | ldmd2    |
| Fortran   | N/A          | 6546.6,-        | 3512.8,-       | 3737.4,-        | 59,-          | 18.2,-           | 20.5,-                | 141.1,-           | 16.2.1                          | gfortran |
| Go        | N/A          | N/A             | N/A            | 609.2,474.6     | 78,69         | N/A              | 29.9,30.6             | 188.9,188.9       | 1.27.1-X:nodwarf5               | go       |
| Hare      | N/A          | 240.9,-         | N/A            | 198.1,-         | 48,-          | 110.7,-          | 110.8,-               | 222.0,-           | 0.26.0.1                        | hare     |
| Haskell   | N/A          | 4458.3,6402.0   | N/A            | 4224.6,4655.1   | 599,568       | 50.7,66.9        | 64.7,79.6             | 654.6,614.1       | 9.6.6                           | ghc      |
| Java      | N/A          | 95.8,-          | N/A            | N/A             | N/A           | 7.2,-            | 14.4,-                | N/A               | 27                              | javac    |
| Julia     | N/A          | N/A             | N/A            | 536.2,648.5     | N/A           | N/A              | 12.7,12.2             | N/A               | 1.14.0-DEV                      | julia    |
| Nim       | N/A          | 95.8,150.0      | N/A            | 846.9,655.6     | 247,212       | 7.7,15.4         | sampling error,51.7   | 178.0,181.4       | 2.2.12                          | nim      |
| OCaml     | N/A          | N/A             | N/A            | 248.2,-         | 39,-          | N/A              | 20.4,-                | N/A               | 5.5.0                           | ocamlc   |
| OCaml     | N/A          | N/A             | N/A            | 1069.3,-        | 169,-         | N/A              | sampling error,-      | 646.1,-           | 5.5.0                           | ocamlopt |
| Odin      | N/A          | 24.5,39.7       | N/A            | 96.2,120.1      | 208,100       | 20.3,32.0        | 40.6,51.4             | 112.6,132.6       | dev-2026-09:a2fb372b7           | odin     |
| Pascal    | N/A          | 134.0,-         | 157.5,-        | 219.0,-         | 166,-         | 18.0,-           | 24.4,-                | 68.8,-            | 3.2.2                           | fpc      |
| Python    | N/A          | 79.1,91.9       | 82.8,91.2      | 80.9,84.8       | 13629,15468   | 11.2,12.3        | 12.7,14.4             | N/A               | 3.12.14                         | pypy3    |
| Python    | N/A          | 43.4,60.0       | 45.4,62.1      | 43.4,47.5       | 3768,5804     | 11.3,14.7        | 11.4,14.7             | N/A               | 3.14.7                          | python   |
| Python    | N/A          | 39.8,58.2       | 45.7,60.4      | 43.3,47.3       | 3800,6931     | 11.3,14.7        | 11.4,14.7             | N/A               | 3.14.7                          | python3  |
| Rust      | N/A          | 97.7,151.0      | N/A            | 312.2,304.0     | 225,154       | 16.2,18.1        | 30.4,28.4             | 360.2,300.1       | 1.100.0-nightly                 | rustc    |
| Scheme    | N/A          | 15.3,-          | 297.2,-        | 268.8,-         | 16610,-       | 1.4,-            | 11.9,-                | N/A               | 10.3.0                          | chez     |
| Swift     | N/A          | 852.8,1741.4    | N/A            | 1091.7,1945.1   | 195,151       | 20.4,25.6        | 30.1,49.1             | 208.3,534.8       | 6.4                             | swiftc   |
| V         | N/A          | N/A             | N/A            | 861.0,1177.8    | 419,115       | N/A              | 31.3,sampling error   | 132.3,132.2       | 0.5.0                           | v        |
| Zig       | 4.2,7.3      | 24.4,36.8       | 189.4,159.0    | 223.7,178.6     | 139,112       | 5.0,5.6          | 10.0,12.7             | 1500.6,1520.5     | 0.17.0-dev.2163+89ff10d56       | zig      |

---

## Conclusions (from sample run shown above)

The Tiny C Compiler (TCC) (`tcc`) is by a large margin the fastest compiler in build speed, followed by the C compiler Cuik and D's `dmd`. TCC's vastly superior build speed stems from its single-pass code-generation architecture: because C relies on explicit forward declarations, the compiler does not need multi-pass symbol resolution, effectively limiting AST parsing, memory allocation, and code generation scope to a single function at a time.

In non-generic checking, `dmd` (3.0x), `gcc` (5.7x), and `clang++` (10.4x) are among the fastest compiled languages relative to TCC. When switching to generic code (normalized to `dmd` = 1.0x), `clang++` remains competitive at 3.8× DMD check time, while `g++-15` and `g++` (16) require roughly 6.8–6.9× DMD check time. Rust (`rustc`) performs significantly better relative to the field in generic mode (8.2× `dmd` build time vs. 72.2× `tcc` in non-generic mode).

The performance of both GCC and Clang sometimes worsen with a newer release.

Both OCaml and Julia scale poorly on deeply nested functions with large synthetic function counts, an explicit maximum limit is therefore enforced. Moreover, the Nim compiler has a hard limit of 50 recursive generic instantiations so therefore `--function-depth` is automatically truncated down to 50.

---

## References

- [Go compilation times compared to C++, D, Rust, Pascal (cross-posted)](https://www.reddit.com/r/golang/comments/55k7n4/go_compilation_times_compared_to_c_d_rust_pascal/)
- [LanguageCompilationSpeed](https://wiki.alopex.li/LanguageCompilationSpeed)
