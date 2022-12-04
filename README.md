# compiler-benchmark

Benchmarks compilation speeds of different combinations of languages and
compilers. Supported languages are:

## Languages with Natives Compilers

- [C](https://en.wikipedia.org/wiki/C_(programming_language)) (using [`gcc`](https://gcc.gnu.org/), [`clang`](https://clang.llvm.org/), [`cproc`](https://github.com/michaelforney/cproc), and [`tcc`](https://bellard.org/tcc/)),
- [C\+\+](http://www.cplusplus.org/) (using [`g++`](https://gcc.gnu.org/) and [`clang++`](https://clang.llvm.org/)),
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
different levels of caching more fair.

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

The compilers `vox` `dmd` are, by a large margin, the fastest. 2 times faster
than its closers competitor, `tcc`. Note that Vox is an experimental language.

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

## Sample run output

The output on my AMD Ryzen Threadripper 3960X 24-Core Processor running Ubuntu
20.04 for the sample call

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
- Add installer V and include a recent build.
- Add language Fortran.
- Add language Pony.
- Sort table primarily by build time and then check time.
- Don’t include Build Time and Build RSS columns when build op is not used.
- Don’t include Check Time and Check RSS columns when check op is not used.

## References

- [Go compilation times compared to C++, D, Rust, Pascal (cross-posted)](https://www.reddit.com/r/golang/comments/55k7n4/go_compilation_times_compared_to_c_d_rust_pascal/)
- [LanguageCompilationSpeed](https://wiki.alopex.li/LanguageCompilationSpeed)
