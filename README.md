# compiler-benchmark

Benchmarks compilation speeds of different combinations of languages and
compilers. Supported languages are:

## Languages with Natives Compilers

- [C](https://en.wikipedia.org/wiki/C_(programming_language)) (using
  [`gcc`](https://gcc.gnu.org/), [`clang`](https://clang.llvm.org/),
  [`cproc`](https://github.com/michaelforney/cproc),
  [`Cuik`](https://github.com/RealNeGate/Cuik/), and
  [`tcc`](https://bellard.org/tcc/)),
- [C\+\+](http://www.cplusplus.org/) (using [`g++`](https://gcc.gnu.org/) and
  [`clang++`](https://clang.llvm.org/)),
- [D](https://dlang.org/) (using `dmd` `ldmd2`, and `gdc`),
- [Go](https://golang.org/) (using `go` or `gccgo`),
- [Swift](https://swift.org/) (using `swiftc`),
- [Rust](https://www.rust-lang.org/) (using `rustc`),
- [Nim](https://nim-lang.org/) (using `nim`),
- [Julia](https://julialang.org/) (using `julia`),
- [Ada](https://en.wikipedia.org/wiki/Ada_(programming_language)) (using `gnatgcc`),
- [Zig](https://ziglang.org/) (using `zig`), and
- [V](https://vlang.io/) (using `v`),
- [Vox](https://github.com/MrSmith33/vox) (using `vox`),
- [C3](https://github.com/c3lang/c3c) (using `c3c`),
- [Pareas](https://github.com/Snektron/pareas) (using `pareas`),
- [Python](https://www.python.org/) (using `python`),
- [Mojo](https://www.modular.com/mojo) (using `mojo`),
- [Scheme](https://cisco.github.io/ChezScheme/) (using `scheme`),

## Languages with Bytecode Compilers:

- [OCaml](https://ocaml.org/) (using `ocamlopt`),
- [C#](https://docs.microsoft.com/en-us/dotnet/csharp/) (using `mcs`), and
- [Java](https://www.oracle.com/java/) (using `javac`).

A subset of these can be installed on Ubuntu (tested on 20.04) via the script
`./install-compilers-on-ubuntu-20.04.sh` in this repo.

## Install Python 3 packages

./install-python-packages.sh

## How it works

A benchmark is typically performed as

    ./benchmark \
        --function-count=$FUNCTION_COUNT \
        --function-depth=$FUNCTION_DEPTH \
        --run-count=5

for suitable values of `$FUNCTION_COUNT` and `FUNCTION_DEPTH` or simply

    ./benchmark

for defaulted values of all the parameters.

A subset of languages combined with set of compilers to benchmark can be chosen
as, for instance,

    ./benchmark --languages=C:tcc,C:gcc,C++,D:dmd,D:ldmd2,D:gdc,Rust

This will generate code into the directory `generated` and then, for each
combination of language, operation type and compiler, run the supported
benchmarks. At the end a Markdown-formatted table showing the results of the
benchmark is printed to standard output. Note that the compilation times in this
table are titled `Time [us/#fn]` meaning in unit microseconds normalized with
number of test functions generated, that is divided by `args.function_count *
args.function_depth`).

GCC and Clang doesn't perform all semantic checks for C++ (because it's too
costly). This is in contrast to D's and Rust's compilers that perform all of
them.

## Sample generated code

To understand how the code generation works we can, for instance, do

    ./benchmark --function-count=3 --function-depth=2 --run-count=5

This will, for the C language case, generate a file `generated/c/main.c` containing

```C
long add_long_n0_h0(long x) { return x + 15440; }
long add_long_n0(long x) { return x + add_long_n0_h0(x) + 95485; }

long add_long_n1_h0(long x) { return x + 37523; }
long add_long_n1(long x) { return x + add_long_n1_h0(x) + 92492; }

long add_long_n2_h0(long x) { return x + 39239; }
long add_long_n2(long x) { return x + add_long_n2_h0(x) + 12248; }


int main(__attribute__((unused)) int argc, __attribute__((unused)) char* argv[]) {
    long long_sum = 0;
    long_sum += add_long_n0(0);
    long_sum += add_long_n1(1);
    long_sum += add_long_n2(2);
    return long_sum;
}
```

### Compiler Object Caches

The numerical constants are randomized using a new seed upon every call. This
makes it impossible for any compiler to utilize any caching mechanism upon
successive calls with same flags that affect the source generation. The purpose
of this is to make the comparison between compilers with no or different
levels of caching more fair.

The caching of the Go reference compiler `go`, for instance, is effectively
disabled by this randomization.

## Generics

For each languages `$LANG` that supports generics an additional templated source
file `main_t.$LANG` will be generated alongside `main.$LANG` equivalent to
the contents of `main.$LANG` apart from that all functions (except `main`) are
templated. This templated source will be benchmarked aswell. The column
**Templated** in the table below indicates whether or not the compilation is
using templated functions.

## Conclusions (from sample run shown below)

TCC build speed is varstly superior because of its single-pass code-generation
architecture. Partly because parsing the C programming language that doesn’t
have to deal with forward declarations and thereby limiting the parsing (and
memory allocation) scope to a single function.

The Tiny C compiler (TCC) (`tcc`) is by a large margin, the fastest, closely
followed by the C compiler Cuik, Vox and D's `dmd`. Note that Vox is an
experimental language and Cuik is an experimental C compiler.

The performance of both GCC and Clang gets significanly worse with each new
release (currently 8, 9, 10 in the table below).

The templated (generic) C++ source checks about 3 times slower than the
non-generic one using `gcc-8` but only about 2.3 times slower for `gcc-10`. For
`clang++-10` the slowdown is only about 1.6. The corresponding slowdown for
generic D (`dmd`) is about 2.5 times. On the other hand, the generic Rust
version interestingly is processed 2-3 times faster than the non-generic
version.

Julia's JIT-compiler is (currently) very memory hungry. A maximum recommended
product of `function-count` and `function-depth` for Julia is 5000. Julia will
therefore be excluded from the benchmark when this maximum is reached.

OCaml's optimizing native compiler `ocamlopt` is very slow for large inputs and
is therefore disabled when the product of `function-count` and `function-depth`
exceeds 10000.

## Sample Run on AMD Ryzen Threadripper 3960X 24-Core

The output on an AMD Ryzen Threadripper 3960X 24-Core Processor running Ubuntu
22.04 for the sample call

    ./benchmark --function-count=200 --function-depth=200 --run-count=1

results in the following table (copied from the output at the end).

| Lang-uage | Temp-lated | AST-Chk Time [us/fn] | Chk Time [us/fn] | Cmp Time [us/fn] | Bld Time [us/fn] | Run Time [us/fn] | Chk RSS [kB/fn] | Bld RSS [kB/fn] | Version | Exec |
| :-------: | ---------- | :------------------: | :--------------: | :--------------: | :--------------: | :--------------: | :-------------: | :-------------: | :-----: | :--: |
| Zig       | No         |    3.6 (best)        |   17.6 (8.7x)    |   94.5 (46.6x)   |   97.4 (43.2x)   |    100 (2.4x)    |    4.4 (7.6x)   |    8.8 (15.9x)  | 0.16.0-dev.1484+d0ba6642b | zig  |
| Zig       | Yes        |    4.4 (1.2x)        |   20.5 (10.2x)   |   99.6 (49.2x)   |  103.1 (45.8x)   |     87 (2.1x)    |    5.1 (8.8x)   |   10.8 (19.5x)  | 0.16.0-dev.1484+d0ba6642b | zig  |
| Vox       | No         |    N/A               |    8.8 (4.3x)    |    N/A           |    6.7 (3.0x)    |    110 (2.6x)    |    1.3 (2.2x)   |    3.7 (6.7x)   | master  | vox  |
| Vox       | Yes        |    N/A               |   11.8 (5.9x)    |    N/A           |    7.3 (3.2x)    |     45 (1.1x)    |    2.3 (3.9x)   |    4.4 (7.9x)   | master  | vox  |
| D         | No         |    N/A               |    8.5 (4.2x)    |   21.0 (10.4x)   |   24.8 (11.0x)   |    112 (2.6x)    |    4.7 (8.0x)   |   16.1 (29.0x)  | v2.112.0-beta.1-616-g6c89bf15e2 | dmd  |
| D         | No         |    N/A               |    6.0 (3.0x)    |  104.4 (51.5x)   |  113.4 (50.4x)   |    167 (4.0x)    |    8.2 (14.0x)  |   21.5 (38.8x)  | 1.42.0-git-3883e04 | ldmd2 |
| D         | Yes        |    N/A               |   17.1 (8.5x)    |   32.0 (15.8x)   |   37.2 (16.5x)   |     60 (1.4x)    |   12.5 (21.4x)  |   24.2 (43.6x)  | v2.112.0-beta.1-616-g6c89bf15e2 | dmd  |
| D         | Yes        |    N/A               |   13.6 (6.7x)    |  117.5 (58.0x)   |  121.7 (54.0x)   |     65 (1.5x)    |   16.7 (28.5x)  |   30.8 (55.4x)  | 1.42.0-git-3883e04 | ldmd2 |
| C         | No         |    N/A               |    2.0 (best)    |    2.0 (best)    |    2.3 (best)    |     43 (1.0x)    |    0.6 (best)   |    0.6 (best)   | 0.9.28rc | tcc  |
| C         | No         |    N/A               |    7.8 (3.8x)    |  248.2 (122.5x)  |  248.6 (110.4x)  |    118 (2.8x)    |    3.0 (5.2x)   |   17.0 (30.6x)  | 15.2.0  | gcc  |
| C         | No         |    N/A               |   10.2 (5.1x)    |  301.7 (148.9x)  |  307.6 (136.6x)  |     80 (1.9x)    |    3.0 (5.1x)   |   14.0 (25.1x)  | 12.5.0  | gcc-12 |
| C         | No         |    N/A               |    7.5 (3.7x)    |  241.6 (119.2x)  |  241.9 (107.4x)  |     89 (2.1x)    |    2.9 (4.9x)   |   15.0 (27.0x)  | 14.3.0  | gcc-14 |
| C         | No         |    N/A               |    7.8 (3.9x)    |  249.0 (122.9x)  |  248.3 (110.2x)  |    125 (3.0x)    |    3.1 (5.3x)   |   17.0 (30.6x)  | 15.2.0  | gcc-15 |
| C         | No         |    N/A               |   21.6 (10.7x)   |  112.9 (55.8x)   |  114.1 (50.7x)   |    166 (3.9x)    |    3.1 (5.3x)   |   11.4 (20.5x)  | 20.1.8  | clang |
| C         | No         |    N/A               |   22.8 (11.3x)   |  113.2 (55.9x)   |  114.5 (50.8x)   |    150 (3.5x)    |    2.8 (4.8x)   |   10.2 (18.3x)  | 17.0.0  | clang-17 |
| C++       | No         |    N/A               |   17.1 (8.5x)    |  263.9 (130.3x)  |  264.9 (117.6x)  |    114 (2.7x)    |    6.2 (10.6x)  |   20.5 (36.9x)  | 15.2.0  | g++  |
| C++       | No         |    N/A               |   22.7 (11.2x)   |  318.3 (157.1x)  |  318.0 (141.2x)  |     93 (2.2x)    |    4.7 (8.1x)   |   16.8 (30.2x)  | 12.5.0  | g++-12 |
| C++       | No         |    N/A               |   16.9 (8.4x)    |  253.5 (125.1x)  |  255.9 (113.6x)  |    127 (3.0x)    |    5.6 (9.5x)   |   18.5 (33.4x)  | 14.3.0  | g++-14 |
| C++       | No         |    N/A               |   17.5 (8.7x)    |  264.8 (130.7x)  |  264.4 (117.4x)  |    115 (2.7x)    |    6.2 (10.5x)  |   20.5 (36.9x)  | 15.2.0  | g++-15 |
| C++       | No         |    N/A               |   29.1 (14.4x)   |  126.0 (62.2x)   |  127.0 (56.4x)   |     89 (2.1x)    |    3.2 (5.5x)   |   11.3 (20.4x)  | 20.1.8  | clang |
| C++       | No         |    N/A               |   30.7 (15.2x)   |  125.1 (61.7x)   |  126.6 (56.2x)   |    162 (3.8x)    |    2.9 (5.0x)   |   10.2 (18.4x)  | 17.0.0  | clang-17 |
| C++       | Yes        |    N/A               |   33.2 (16.4x)   |  313.6 (154.8x)  |  311.8 (138.4x)  |     46 (1.1x)    |    9.9 (17.0x)  |   20.6 (37.1x)  | 15.2.0  | g++  |
| C++       | Yes        |    N/A               |   42.8 (21.2x)   |  384.5 (189.8x)  |  375.8 (166.8x)  |     73 (1.7x)    |    8.3 (14.2x)  |   20.9 (37.6x)  | 12.5.0  | g++-12 |
| C++       | Yes        |    N/A               |   31.9 (15.8x)   |  303.9 (150.0x)  |  304.1 (135.0x)  |     54 (1.3x)    |    9.0 (15.3x)  |   20.2 (36.4x)  | 14.3.0  | g++-14 |
| C++       | Yes        |    N/A               |   32.5 (16.1x)   |  315.0 (155.5x)  |  308.5 (136.9x)  |     42 (best)    |    9.9 (17.0x)  |   20.6 (37.1x)  | 15.2.0  | g++-15 |
| C++       | Yes        |    N/A               |   46.3 (22.9x)   |  129.1 (63.7x)   |  127.7 (56.7x)   |     63 (1.5x)    |    5.1 (8.7x)   |   13.7 (24.6x)  | 20.1.8  | clang |
| C++       | Yes        |    N/A               |   47.7 (23.6x)   |  130.5 (64.4x)   |  128.7 (57.1x)   |     48 (1.1x)    |    4.9 (8.3x)   |   12.6 (22.7x)  | 17.0.0  | clang-17 |
| Go        | No         |    N/A               |   14.4 (7.2x)    |    N/A           |    N/A           |    N/A           |    4.4 (7.5x)   |    N/A          | 1.24.4  | gotype |
| N/A       | N/A        |    N/A               |    N/A           |    N/A           |    N/A           |    N/A           |    7.4 (12.6x)  |   29.5 (53.1x)  | N/A     | N/A  |
| Go        | No         |    N/A               |    N/A           |    N/A           |  181.7 (80.6x)   |     95 (2.2x)    |    N/A          |   26.9 (48.4x)  | 1.24.4  | go   |
| Swift     | No         |    N/A               |  760.0 (376.6x)  |    N/A           | 1100.8 (488.7x)  |    139 (3.3x)    |   10.8 (18.5x)  |   26.6 (47.9x)  | 6.2.1   | swiftc |
| V         | No         |    N/A               |    N/A           |    N/A           |   26.8 (11.9x)   |    141 (3.3x)    |    N/A          |   16.2 (29.1x)  | 0.4.12  | v    |
| V         | Yes        |    N/A               |    N/A           |    N/A           |  490.6 (217.8x)  |    126 (3.0x)    |    N/A          |  151.2 (272.1x) | 0.4.12  | v    |
| C3        | No         |  109.0 (30.3x)       |    N/A           |    N/A           |  109.0 (48.4x)   |     97 (2.3x)    |    1.5 (2.6x)   |   17.2 (30.9x)  | 0.7.9   | c3c  |
| Rust      | No         |    N/A               |   69.2 (34.3x)   |    N/A           |  147.1 (65.3x)   |    197 (4.7x)    |   14.0 (24.0x)  |   24.1 (43.3x)  | 1.94.0-nightly | rustc |
| Rust      | Yes        |    N/A               |   82.3 (40.8x)   |    N/A           |  140.6 (62.4x)   |    116 (2.7x)    |   15.1 (25.9x)  |   19.1 (34.3x)  | 1.94.0-nightly | rustc |
| Nim       | No         |    N/A               |   53.3 (26.4x)   |    N/A           |  395.2 (175.4x)  |    138 (3.3x)    |    4.2 (7.3x)   | sampling error  | 2.2.6   | nim  |
| C#        | No         |    N/A               |    N/A           |    N/A           |   22.0 (9.7x)    |  19007 (449.2x)  |    N/A          |    4.5 (8.1x)   | 6.12.0.199 | mcs  |
| C#        | No         |    N/A               |    N/A           |    N/A           |   21.9 (9.7x)    |  18955 (447.9x)  |    N/A          |    4.7 (8.4x)   | error   | mono-csc |
| Java      | No         |    N/A               |   18.8 (9.3x)    |    N/A           |    N/A           |    N/A           |    7.4 (12.6x)  |   17.5 (31.5x)  | 26-ea   | javac |
| Python    | No         |    N/A               |   18.9 (9.4x)    |    N/A           |    N/A           |    N/A           |    8.1 (13.9x)  |    8.0 (14.4x)  | 3.13.7  | python3 |
| Python    | Yes        |    N/A               |   18.9 (9.4x)    |    N/A           |    N/A           |    N/A           |    8.1 (13.9x)  |    8.0 (14.4x)  | 3.13.7  | python3 |
| OCaml     | No         |    N/A               |    N/A           |    N/A           |  573.7 (254.7x)  |    236 (5.6x)    |    N/A          |   48.7 (87.6x)  | 5.3.0   | ocamlopt |
| OCaml     | No         |    N/A               |    N/A           |    N/A           |   96.0 (42.6x)   |     59 (1.4x)    |    N/A          |   19.7 (35.4x)  | 5.3.0   | ocamlc |
| Julia     | No         |    N/A               |    N/A           |    N/A           |  382.8 (169.9x)  |    N/A           |    N/A          |   12.4 (22.4x)  | 1.14.0-DEV | julia |
| Julia     | Yes        |    N/A               |    N/A           |    N/A           |  312.8 (138.9x)  |    N/A           |    N/A          |   11.6 (20.9x)  | 1.14.0-DEV | julia |
| Scheme    | No         |    N/A               |    N/A           |    N/A           |  260.5 (115.7x)  |    N/A           |    N/A          |   unavailable   | 10.0.0  | scheme |

## Sample Run on Intel Core (Tiger Lake R0) [Willow Cove] {Sunny Cove}, 10nm++

The output on a Intel Core (Tiger Lake R0) [Willow Cove] {Sunny Cove}, 10nm++
running Ubuntu 22.04 for the sample call

    ./benchmark --function-count=200 --function-depth=200 --run-count=5

results in the following table (copied from the output at the end).

| Lang-uage | Temp-lated | Check Time [us/fn] | Compile Time [us/fn] | Build Time [us/fn] | Run Time [us/fn] | Check RSS [kB/fn] | Build RSS [kB/fn] | Exec Version | Exec Path |
| :-------: | ---------- | :----------------: | :------------------: | :----------------: | :--------------: | :---------------: | :---------------: | :----------: | :-------: |
| D         | No         |    5.7 (4.1x)      |   14.4 (10.7x)       |   16.2 (11.5x)     |     46 (3.1x)    |    5.0 (10.6x)    |   14.7 (31.6x)    | v2.107.0-beta.1-136-gc5c4def18f | dmd       |
| D         | No         |    4.3 (3.1x)      |   67.5 (50.4x)       |   68.2 (48.6x)     |    218 (14.6x)   |    6.3 (13.5x)    |   20.8 (44.8x)    | 1.36.0       | ldmd2     |
| D         | No         |    4.7 (3.4x)      |  186.6 (139.3x)      |  183.8 (130.8x)    |     37 (2.5x)    |    4.8 (10.2x)    |   19.5 (41.9x)    | 11.4.0       | gdc       |
| D         | Yes        |   17.4 (12.6x)     |   29.1 (21.7x)       |   30.9 (22.0x)     |     45 (3.0x)    |   13.8 (29.6x)    |   23.8 (51.2x)    | v2.107.0-beta.1-136-gc5c4def18f | dmd       |
| D         | Yes        |   17.2 (12.5x)     |   83.0 (61.9x)       |   83.2 (59.2x)     |    217 (14.5x)   |   15.3 (32.9x)    |   29.6 (63.6x)    | 1.36.0       | ldmd2     |
| D         | Yes        |   11.0 (8.0x)      |  195.8 (146.1x)      |  192.6 (137.0x)    |     34 (2.3x)    |   13.6 (29.1x)    |   29.1 (62.5x)    | 11.4.0       | gdc       |
| C         | No         |    1.4 (best)      |    1.3 (best)        |    1.4 (best)      |     15 (best)    |    0.5 (best)     |    0.5 (best)     | 0.9.28rc     | tcc       |
| C         | No         |    4.1 (3.0x)      |   27.9 (20.8x)       |   29.7 (21.1x)     |    275 (18.4x)   |    4.6 (10.0x)    |   49.7 (106.8x)   | ~master      | cuik      |
| C         | No         |    8.0 (5.8x)      |  220.7 (164.7x)      |  219.1 (155.9x)    |     22 (1.5x)    |    3.0 (6.5x)     |   14.0 (30.1x)    | 12.3.0       | gcc       |
| C         | No         |    6.1 (4.4x)      |  173.8 (129.7x)      |  174.2 (124.0x)    |     22 (1.4x)    |    2.8 (6.0x)     |   14.4 (30.9x)    | 11.4.0       | gcc-11    |
| C         | No         |    8.0 (5.8x)      |  221.6 (165.4x)      |  221.1 (157.4x)    |     22 (1.5x)    |    3.0 (6.5x)     |   14.0 (30.1x)    | 12.3.0       | gcc-12    |
| C         | No         |   13.5 (9.8x)      |   84.3 (62.9x)       |   85.8 (61.1x)     |    347 (23.2x)   |    2.9 (6.1x)     |   10.8 (23.3x)    | 14.0.0-1     | clang     |
| C         | No         |   13.3 (9.6x)      |   81.7 (61.0x)       |   83.5 (59.4x)     |    183 (12.2x)   |    2.2 (4.8x)     |    9.7 (20.9x)    | 13.0.0       | clang-13  |
| C         | No         |   13.6 (9.8x)      |   83.8 (62.5x)       |   85.7 (61.0x)     |    313 (21.0x)   |    2.8 (6.1x)     |   10.8 (23.3x)    | 14.0.0-1     | clang-14  |
| C         | No         |   13.9 (10.1x)     |   82.1 (61.3x)       |   83.9 (59.7x)     |    320 (21.4x)   |    2.9 (6.3x)     |   10.8 (23.1x)    | 15.0.7       | clang-15  |
| C         | No         |   14.5 (10.5x)     |   86.7 (64.7x)       |   87.9 (62.6x)     |    257 (17.2x)   |    2.8 (6.0x)     |   10.9 (23.5x)    | 17.0.6       | clang-17  |
| C++       | No         |   18.0 (13.0x)     |  229.2 (171.1x)      |  231.4 (164.7x)    |     27 (1.8x)    |    4.8 (10.3x)    |   16.8 (36.1x)    | 12.3.0       | g++       |
| C++       | No         |   12.7 (9.2x)      |  185.4 (138.3x)      |  185.0 (131.7x)    |     23 (1.5x)    |    4.5 (9.7x)     |   14.3 (30.7x)    | 11.4.0       | g++-11    |
| C++       | No         |   18.2 (13.2x)     |  229.4 (171.2x)      |  231.5 (164.7x)    |     22 (1.5x)    |    4.7 (10.2x)    |   16.8 (36.1x)    | 12.3.0       | g++-12    |
| C++       | No         |   17.3 (12.6x)     |   90.6 (67.6x)       |   93.3 (66.4x)     |    347 (23.2x)   |    3.0 (6.4x)     |   10.8 (23.3x)    | 14.0.0-1     | clang     |
| C++       | No         |   17.2 (12.5x)     |   88.9 (66.4x)       |   91.0 (64.8x)     |    180 (12.0x)   |    2.4 (5.1x)     |    9.8 (21.0x)    | 13.0.0       | clang-13  |
| C++       | No         |   17.5 (12.7x)     |   90.8 (67.8x)       |   93.3 (66.4x)     |    312 (20.9x)   |    3.0 (6.4x)     |   10.8 (23.3x)    | 14.0.0-1     | clang-14  |
| C++       | No         |   18.2 (13.2x)     |   89.5 (66.8x)       |   91.9 (65.4x)     |    297 (19.9x)   |    3.0 (6.5x)     |   10.8 (23.3x)    | 15.0.7       | clang-15  |
| C++       | No         |   18.3 (13.2x)     |   94.6 (70.6x)       |   96.4 (68.6x)     |    278 (18.6x)   |    2.9 (6.2x)     |   10.9 (23.5x)    | 17.0.6       | clang-17  |
| C++       | Yes        |   34.7 (25.2x)     |  274.7 (205.0x)      |  287.4 (204.5x)    |     21 (1.4x)    |    8.3 (17.8x)    |   20.9 (45.0x)    | 12.3.0       | g++       |
| C++       | Yes        |   27.7 (20.1x)     |  227.3 (169.6x)      |  240.8 (171.4x)    |     22 (1.5x)    |    8.2 (17.7x)    |   20.8 (44.7x)    | 11.4.0       | g++-11    |
| C++       | Yes        |   34.5 (25.0x)     |  275.0 (205.3x)      |  288.0 (205.0x)    |     23 (1.5x)    |    8.3 (17.8x)    |   20.9 (45.0x)    | 12.3.0       | g++-12    |
| C++       | Yes        |   28.4 (20.6x)     |   99.1 (73.9x)       |  113.2 (80.6x)     |    351 (23.5x)   |    4.8 (10.3x)    |   14.0 (30.2x)    | 14.0.0-1     | clang     |
| C++       | Yes        |   28.3 (20.5x)     |   98.3 (73.4x)       |  112.4 (80.0x)     |    179 (12.0x)   |    4.2 (9.0x)     |   13.2 (28.3x)    | 13.0.0       | clang-13  |
| C++       | Yes        |   28.6 (20.7x)     |   98.6 (73.6x)       |  113.3 (80.6x)     |    347 (23.2x)   |    4.8 (10.3x)    |   14.0 (30.2x)    | 14.0.0-1     | clang-14  |
| C++       | Yes        |   29.7 (21.5x)     |   98.3 (73.4x)       |  112.4 (80.0x)     |    319 (21.3x)   |    4.9 (10.4x)    |   14.2 (30.5x)    | 15.0.7       | clang-15  |
| C++       | Yes        |   30.5 (22.1x)     |  102.9 (76.8x)       |  116.8 (83.1x)     |    275 (18.4x)   |    4.8 (10.3x)    |   14.2 (30.6x)    | 17.0.6       | clang-17  |
| Ada       | No         |    N/A             |    N/A               |  752.0 (535.2x)    |     38 (2.5x)    |    N/A            |   31.8 (68.4x)    | 12.3.0       | gnat      |
| Ada       | No         |    N/A             |    N/A               |  755.5 (537.7x)    |     40 (2.7x)    |    N/A            |   31.8 (68.4x)    | 12.3.0       | gnat-12   |
| Go        | No         |    8.1 (5.9x)      |    N/A               |    N/A             |    N/A           |    4.3 (9.3x)     |    N/A            | 1.21.6       | gotype    |
| Go        | No         |    N/A             |    N/A               |  344.1 (244.9x)    |     24 (1.6x)    |    7.2 (15.5x)    |   23.9 (51.3x)    | 12.3.0       | gccgo-12  |
| Go        | No         |    N/A             |    N/A               |  113.8 (81.0x)     |     57 (3.8x)    |    N/A            |   27.5 (59.2x)    | 1.21.6       | go        |
| Swift     | No         |  429.3 (311.0x)    |    N/A               |  679.0 (483.2x)    |    913 (61.1x)   |    9.3 (20.1x)    |   24.2 (51.9x)    | 5.9.2        | swiftc    |
| Zig       | No         |   12.1 (8.8x)      |    N/A               |  226.2 (161.0x)    |    106 (7.1x)    |    3.1 (6.7x)     |   27.2 (58.4x)    | 0.12.0-dev.2341+92211135f | zig       |
| Zig       | Yes        |   14.1 (10.2x)     |    N/A               |  232.9 (165.8x)    |     78 (5.2x)    |    3.5 (7.5x)     |   27.7 (59.6x)    | 0.12.0-dev.2341+92211135f | zig       |
| Rust      | No         |   28.1 (20.4x)     |    N/A               |  157.2 (111.9x)    |    680 (45.5x)   |   14.5 (31.2x)    |   33.1 (71.1x)    | 1.77.0-nightly | rustc     |
| Rust      | Yes        |   41.4 (30.0x)     |    N/A               |  116.2 (82.7x)     |    726 (48.7x)   |   16.9 (36.2x)    |   26.8 (57.6x)    | 1.77.0-nightly | rustc     |
| Nim       | No         |   36.3 (26.3x)     |    N/A               |  358.5 (255.2x)    |     60 (4.0x)    |    4.4 (9.4x)     | sampling error    | 2.0.2        | nim       |
| C#        | No         |    N/A             |    N/A               |   15.5 (11.1x)     |    349 (23.4x)   |    N/A            |    4.7 (10.1x)    | 6.12.0.200   | mcs       |
| C#        | No         |    N/A             |    N/A               |  182.2 (129.6x)    |   1477 (98.9x)   |    N/A            |    8.8 (19.0x)    | 3.9.0-6.21124.20 | csc       |
| N/A       | N/A        |    N/A             |    N/A               |    N/A             |    N/A           |    N/A            |   12.6 (27.2x)    | N/A          | N/A       |
| N/A       | N/A        |    N/A             |    N/A               |    N/A             |    N/A           |    N/A            |   17.2 (37.0x)    | N/A          | N/A       |
| OCaml     | No         |    N/A             |    N/A               |   82.0 (58.3x)     |     19 (1.3x)    |    N/A            |   16.0 (34.3x)    | 4.13.1       | ocamlc    |
| Julia     | No         |    N/A             |    N/A               |  287.5 (204.6x)    |    N/A           |    N/A            |   12.4 (26.6x)    | 1.11.0-DEV   | julia     |
| Julia     | Yes        |    N/A             |    N/A               |  231.4 (164.6x)    |    N/A           |    N/A            |   10.6 (22.7x)    | 1.11.0-DEV   | julia     |

## TODO

- Add function `benchmark_CSharp_using_dotnet()` that calls `dotnet build`. On
  my Ubuntu 22.04, both `dotnet new` and `dotnet build` segfaults so won’t waste
  time with this for now.
- Add language Fortran.
- Add language Pony.
- Sort table primarily by build time and then check time.
- Don’t include Build Time and Build RSS columns when build op is not used.
- Don’t include Check Time and Check RSS columns when check op is not used.

## References

- [Go compilation times compared to C++, D, Rust, Pascal (cross-posted)](https://www.reddit.com/r/golang/comments/55k7n4/go_compilation_times_compared_to_c_d_rust_pascal/)
- [LanguageCompilationSpeed](https://wiki.alopex.li/LanguageCompilationSpeed)
