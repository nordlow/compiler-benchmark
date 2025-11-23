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

## Sample Run on AMD Ryzen Threadripper 3960X 24-Core

The output on an AMD Ryzen Threadripper 3960X 24-Core Processor running Ubuntu
22.04 for the sample call

    ./benchmark --function-count=200 --function-depth=200 --run-count=1

results in the following table (copied from the output at the end).

| Lang-uage | Temp-lated | Check Time [us/fn] | Compile Time [us/fn] | Build Time [us/fn] | Run Time [us/fn] | Check RSS [kB/fn] | Build RSS [kB/fn] | Exec Version | Exec Path |
| :-------: | ---------- | :----------------: | :------------------: | :----------------: | :--------------: | :---------------: | :---------------: | :----------: | :-------: |
| Vox       | No         |    1.5 (best)      |    N/A               |    5.2 (3.3x)      |     42 (1.2x)    |    1.1 (2.8x)     |    3.6 (8.1x)     | master       | vox       |
| Vox       | Yes        |    2.0 (1.4x)      |    N/A               |    6.1 (3.9x)      |     65 (1.8x)    |    2.0 (5.1x)     |    4.4 (9.9x)     | master       | vox       |
| D         | No         |    6.3 (4.2x)      |   13.4 (7.4x)        |   17.9 (11.4x)     |     72 (2.0x)    |    4.6 (11.5x)    |   12.2 (27.2x)    | v2.097.0-275-g357bc9d7a | dmd       |
| D         | No         |    7.4 (5.0x)      |   90.8 (49.9x)       |   99.6 (63.5x)     |    219 (6.2x)    |    5.7 (14.3x)    |   19.7 (43.8x)    | 1.26.0       | ldmd2     |
| D         | No         |    6.4 (4.3x)      |  240.5 (132.3x)      |  237.5 (151.5x)    |     40 (1.1x)    |    4.5 (11.2x)    |   19.2 (42.6x)    | 10.3.0       | gdc       |
| D         | Yes        |   12.7 (8.5x)      |   21.9 (12.0x)       |   25.9 (16.5x)     |     64 (1.8x)    |   13.0 (32.5x)    |   21.4 (47.6x)    | v2.097.0-275-g357bc9d7a | dmd       |
| D         | Yes        |   14.2 (9.6x)      |  102.0 (56.1x)       |  110.6 (70.6x)     |    302 (8.6x)    |   14.9 (37.4x)    |   29.3 (65.3x)    | 1.26.0       | ldmd2     |
| D         | Yes        |   12.4 (8.3x)      |  287.4 (158.0x)      |  286.8 (182.9x)    |     56 (1.6x)    |   13.2 (33.1x)    |   28.3 (63.0x)    | 10.3.0       | gdc       |
| C         | No         |    1.8 (1.2x)      |    1.8 (best)        |    1.6 (best)      |     44 (1.3x)    |    0.4 (best)     |    0.4 (best)     | 0.9.27       | tcc       |
| C         | No         |    5.3 (3.5x)      |    N/A               |    N/A             |    N/A           |    1.7 (4.2x)     |    N/A            | unknown      | cproc     |
| C         | No         |    8.2 (5.5x)      |  274.2 (150.8x)      |  282.0 (179.8x)    |     55 (1.6x)    |    2.9 (7.4x)     |   14.3 (31.9x)    | 9.3.0        | gcc       |
| C         | No         |    8.2 (5.5x)      |  273.6 (150.4x)      |  278.8 (177.8x)    |     54 (1.5x)    |    3.0 (7.5x)     |   14.3 (31.8x)    | 9.3.0        | gcc-9     |
| C         | No         |    6.0 (4.0x)      |  220.4 (121.2x)      |  224.9 (143.4x)    |     55 (1.6x)    |    2.8 (7.1x)     |   14.3 (31.9x)    | 10.3.0       | gcc-10    |
| C         | No         |   14.7 (9.9x)      |  121.9 (67.0x)       |  125.9 (80.3x)     |   1045 (29.8x)   |    1.8 (4.4x)     |    9.4 (20.9x)    | 10.0.0-4     | clang-10  |
| C         | No         |   15.6 (10.5x)     |  121.7 (66.9x)       |  124.7 (79.5x)     |    376 (10.7x)   |    1.9 (4.7x)     |    9.4 (21.0x)    | 11.0.0-2     | clang-11  |
| C++       | No         |   20.1 (13.5x)     |  290.9 (159.9x)      |  293.3 (187.0x)    |     42 (1.2x)    |    4.4 (11.1x)    |   14.4 (32.1x)    | 9.3.0        | g++       |
| C++       | No         |   19.9 (13.4x)     |  291.9 (160.5x)      |  294.6 (187.9x)    |     48 (1.4x)    |    4.4 (11.0x)    |   14.4 (32.1x)    | 9.3.0        | g++-9     |
| C++       | No         |   14.9 (10.0x)     |  235.8 (129.6x)      |  238.4 (152.0x)    |     35 (best)    |    4.4 (11.1x)    |   14.1 (31.3x)    | 10.3.0       | g++-10    |
| C++       | No         |   21.1 (14.2x)     |  135.2 (74.4x)       |  137.9 (87.9x)     |   1022 (29.1x)   |    1.9 (4.7x)     |    9.5 (21.1x)    | 10.0.0-4     | clang-10  |
| C++       | No         |   21.8 (14.6x)     |  133.8 (73.6x)       |  135.3 (86.3x)     |    314 (8.9x)    |    2.0 (5.0x)     |    9.5 (21.2x)    | 11.0.0-2     | clang-11  |
| C++       | Yes        |   40.0 (26.9x)     |  346.4 (190.5x)      |  370.5 (236.2x)    |     47 (1.3x)    |    7.8 (19.6x)    |   23.6 (52.6x)    | 9.3.0        | g++       |
| C++       | Yes        |   40.0 (26.8x)     |  346.3 (190.4x)      |  362.8 (231.3x)    |     52 (1.5x)    |    7.8 (19.6x)    |   23.6 (52.5x)    | 9.3.0        | g++-9     |
| C++       | Yes        |   31.4 (21.1x)     |  285.9 (157.2x)      |  309.2 (197.2x)    |     45 (1.3x)    |    8.0 (20.2x)    |   21.9 (48.7x)    | 10.3.0       | g++-10    |
| C++       | Yes        |   35.0 (23.5x)     |  152.1 (83.7x)       |  186.4 (118.9x)    |   1049 (29.9x)   |    3.7 (9.2x)     |   14.1 (31.4x)    | 10.0.0-4     | clang-10  |
| C++       | Yes        |   35.8 (24.1x)     |  132.1 (72.6x)       |  168.6 (107.5x)    |    403 (11.5x)   |    3.8 (9.6x)     |   14.3 (31.9x)    | 11.0.0-2     | clang-11  |
| Ada       | No         |    N/A             |    N/A               |  791.2 (504.5x)    |     93 (2.7x)    |    N/A            |   31.8 (70.8x)    | 10.3.0       | gnat      |
| Ada       | No         |    N/A             |    N/A               |  802.8 (511.9x)    |     94 (2.7x)    |    N/A            |   31.8 (70.8x)    | 10.3.0       | gnat-10   |
| Go        | No         |   12.9 (8.7x)      |    N/A               |    N/A             |    N/A           |    3.8 (9.5x)     |    N/A            | 1.16.5       | gotype    |
| Go        | No         |    N/A             |    N/A               |  377.3 (240.6x)    |     48 (1.4x)    |    6.4 (15.9x)    |   24.3 (54.1x)    | 10.3.0       | gccgo-10  |
| Go        | No         |    N/A             |    N/A               |  117.6 (75.0x)     |    119 (3.4x)    |    N/A            |   27.5 (61.1x)    | 1.16.5       | go        |
| Swift     | No         |  349.4 (234.7x)    |    N/A               |  830.0 (529.3x)    |    138 (3.9x)    |    5.9 (14.9x)    |   16.9 (37.5x)    | 5.3.3        | swiftc    |
| V         | No         |    N/A             |    N/A               |   17.9 (11.4x)     |    451 (12.8x)   |    N/A            |   12.1 (27.0x)    | 0.2.2        | v         |
| V         | Yes        |    N/A             |    N/A               |   19.0 (12.1x)     |    402 (11.4x)   |    N/A            |   12.6 (28.0x)    | 0.2.2        | v         |
| Zig       | No         |   62.6 (42.0x)     |    N/A               |  284.8 (181.6x)    |    831 (23.7x)   |   21.7 (54.4x)    |   33.6 (74.8x)    | 0.8.0        | zig       |
| Zig       | Yes        |   81.6 (54.8x)     |    N/A               |  303.5 (193.6x)    |    917 (26.1x)   |   29.9 (74.9x)    |   39.9 (88.7x)    | 0.8.0        | zig       |
| Rust      | No         |  126.0 (84.7x)     |    N/A               |  412.9 (263.3x)    |   1659 (47.3x)   |   13.9 (34.8x)    |   30.3 (67.5x)    | 1.53.0-nightly | rustc     |
| Rust      | Yes        |  140.5 (94.4x)     |    N/A               |  258.2 (164.7x)    |   1766 (50.3x)   |   15.8 (39.6x)    |   21.5 (48.0x)    | 1.53.0-nightly | rustc     |
| Nim       | No         |   36.6 (24.6x)     |    N/A               |   80.3 (51.2x)     |     76 (2.2x)    |    4.2 (10.5x)    |    8.0 (17.8x)    | 1.4.6        | nim       |
| C#        | No         |    N/A             |    N/A               |   25.1 (16.0x)     |    556 (15.8x)   |    N/A            |    4.7 (10.4x)    | 6.12.0.122   | mcs       |
| OCaml     | No         |    N/A             |    N/A               |  898.4 (572.9x)    |    463 (13.2x)   |    N/A            |   40.6 (90.5x)    | 4.08.1       | ocamlopt  |
| OCaml     | No         |    N/A             |    N/A               |   87.7 (55.9x)     |    193 (5.5x)    |    N/A            |   16.5 (36.8x)    | 4.08.1       | ocamlc    |
| Julia     | No         |    N/A             |    N/A               |  384.6 (245.2x)    |    N/A           |    N/A            |   22.7 (50.6x)    | 1.8.0-DEV    | julia     |
| Julia     | Yes        |    N/A             |    N/A               |  331.7 (211.5x)    |    N/A           |    N/A            |   22.5 (50.0x)    | 1.8.0-DEV    | julia     |

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

<!-- Local Variables: -->
<!-- gptel-model: grok-beta -->
<!-- gptel--backend-name: "xAI" -->
<!-- gptel--bounds: nil -->
<!-- End: -->
