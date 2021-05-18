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

A specific subset of support languages can be chosen as, for instance,

    ./benchmark --languages=C++,D,Rust

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

The numerical constants are randomize using a new seed upon every call. This
makes it impossible for any compiler to utilize any caching mechanism upon
successive calls with same flags that affect the source generation. The purpose
of this is to make the comparison between compilers with different levels of
caching more fair.

For instance, the caching mechanism of the Go reference compiler `go` can no
longer be deactivated.

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

| Lang-uage | Temp-lated | Check Time [us/fn] | Build Time [us/fn] | Run Time [us/fn] | Check RSS [kB/fn] | Build RSS [kB/fn] | Exec Version | Exec Path |
| :-------: | ---------- | :----------------: | :----------------: | :--------------: | :---------------: | :---------------: | :----------: | :-------: |
| D         | No         |    6.5 (4.0x)      |   18.4 (10.9x)     |     88 (2.0x)    |    4.3 (10.1x)    |   12.1 (28.1x)    | v2.096.1-206-g564b1feaa | dmd       |
| D         | No         |    7.5 (4.6x)      |   99.9 (59.1x)     |    305 (7.0x)    |    5.6 (13.2x)    |   19.5 (45.1x)    | 1.26.0-beta1 | ldmd2     |
| D         | No         |    6.7 (4.1x)      |  298.1 (176.2x)    |     58 (1.3x)    |    4.5 (10.5x)    |   19.4 (44.9x)    | 10.2.0       | gdc       |
| D         | Yes        |   12.8 (7.9x)      |   26.5 (15.7x)     |     91 (2.1x)    |   13.4 (31.4x)    |   21.3 (49.4x)    | v2.096.1-206-g564b1feaa | dmd       |
| D         | Yes        |   15.1 (9.3x)      |  109.8 (64.9x)     |    305 (7.0x)    |   14.9 (35.0x)    |   29.1 (67.5x)    | 1.26.0-beta1 | ldmd2     |
| D         | Yes        |   14.1 (8.6x)      |  337.6 (199.6x)    |     55 (1.3x)    |   13.3 (31.3x)    |   28.5 (66.0x)    | 10.2.0       | gdc       |
| Vox       | No         |    1.7 (1.0x)      |    5.4 (3.2x)      |     45 (1.0x)    |    1.1 (2.6x)     |    3.6 (8.3x)     | master       | vox       |
| Vox       | Yes        |    2.3 (1.4x)      |    6.1 (3.6x)      |     62 (1.4x)    |    1.8 (4.2x)     |    4.3 (9.9x)     | master       | vox       |
| C         | No         |    1.6 (best)      |    1.7 (best)      |     44 (best)    |    0.4 (best)     |    0.4 (best)     | 0.9.27       | tcc       |
| C         | No         |    8.1 (5.0x)      |  274.8 (162.5x)    |     56 (1.3x)    |    2.9 (6.9x)     |   14.3 (33.1x)    | 9.3.0        | gcc       |
| C         | No         |    8.3 (5.1x)      |  270.8 (160.1x)    |     48 (1.1x)    |    2.9 (6.9x)     |   14.3 (33.2x)    | 9.3.0        | gcc-9     |
| C         | No         |    8.6 (5.3x)      |  280.1 (165.6x)    |     66 (1.5x)    |    3.0 (7.0x)     |   14.4 (33.4x)    | 10.2.0       | gcc-10    |
| C         | No         |   14.4 (8.8x)      |  125.3 (74.1x)     |    962 (22.0x)   |    1.8 (4.1x)     |    9.4 (21.7x)    | 10.0.0-4     | clang-10  |
| C         | No         |   17.3 (10.6x)     |  124.4 (73.6x)     |    428 (9.8x)    |    1.9 (4.4x)     |    9.4 (21.8x)    | 11.0.0-2     | clang-11  |
| C         | No         |    5.7 (3.5x)      |    N/A             |    N/A           |    1.7 (4.0x)     |    N/A            | unknown      | cproc     |
| C++       | No         |   20.3 (12.4x)     |  295.0 (174.4x)    |     44 (1.0x)    |    4.5 (10.6x)    |   14.5 (33.7x)    | 9.3.0        | g++       |
| C++       | No         |   20.1 (12.3x)     |  293.5 (173.5x)    |     51 (1.2x)    |    4.5 (10.5x)    |   14.5 (33.6x)    | 9.3.0        | g++-9     |
| C++       | No         |   20.7 (12.7x)     |  298.1 (176.2x)    |     53 (1.2x)    |    4.3 (10.1x)    |   14.5 (33.6x)    | 10.2.0       | g++-10    |
| C++       | No         |   20.7 (12.7x)     |  136.2 (80.5x)     |    859 (19.6x)   |    1.9 (4.4x)     |    9.5 (22.0x)    | 10.0.0-4     | clang++-10 |
| C++       | No         |   22.2 (13.6x)     |  139.0 (82.2x)     |    444 (10.1x)   |    2.0 (4.6x)     |    9.5 (22.1x)    | 11.0.0-2     | clang++-11 |
| C++       | Yes        |   42.2 (25.9x)     |  360.9 (213.4x)    |     55 (1.3x)    |    7.9 (18.5x)    |   23.7 (54.9x)    | 9.3.0        | g++       |
| C++       | Yes        |   40.6 (24.9x)     |  360.7 (213.2x)    |     51 (1.2x)    |    7.9 (18.5x)    |   23.7 (55.0x)    | 9.3.0        | g++-9     |
| C++       | Yes        |   38.1 (23.3x)     |  378.7 (223.9x)    |     55 (1.3x)    |    7.5 (17.6x)    |   23.3 (53.9x)    | 10.2.0       | g++-10    |
| C++       | Yes        |   33.8 (20.7x)     |  183.6 (108.6x)    |    470 (10.7x)   |    3.7 (8.7x)     |   14.1 (32.7x)    | 10.0.0-4     | clang++-10 |
| C++       | Yes        |   35.4 (21.7x)     |  166.3 (98.3x)     |    355 (8.1x)    |    3.8 (8.9x)     |   14.3 (33.2x)    | 11.0.0-2     | clang++-11 |
| Ada       | No         |    N/A             |  927.2 (548.1x)    |     97 (2.2x)    |    N/A            |   31.8 (73.6x)    | 10.2.0       | gnat      |
| Ada       | No         |    N/A             |  915.4 (541.1x)    |     96 (2.2x)    |    N/A            |   31.8 (73.6x)    | 10.2.0       | gnat-10   |
| Go        | No         |   13.0 (8.0x)      |    N/A             |    N/A           |    3.8 (9.0x)     |    N/A            | 1.16.3       | gotype    |
| Go        | No         |    N/A             |  432.4 (255.6x)    |     52 (1.2x)    |    6.4 (15.1x)    |   24.3 (56.4x)    | 10.2.0       | gccgo-10  |
| Go        | No         |    N/A             |  119.0 (70.4x)     |    133 (3.0x)    |    N/A            |   27.4 (63.5x)    | 1.16.3       | go        |
| Swift     | No         |  340.5 (208.5x)    |  802.7 (474.5x)    |    144 (3.3x)    |    5.9 (13.8x)    |   16.8 (38.9x)    | 5.3.3        | swiftc    |
| V         | No         |    N/A             |   19.3 (11.4x)     |    474 (10.8x)   |    N/A            |   12.0 (27.8x)    | 0.2.2        | v         |
| V         | Yes        |    N/A             |   22.7 (13.4x)     |    440 (10.0x)   |    N/A            |   13.3 (30.7x)    | 0.2.2        | v         |
| Zig       | No         |   64.6 (39.5x)     |  288.3 (170.4x)    |    925 (21.1x)   |   23.7 (55.8x)    |   37.4 (86.7x)    | 0.7.1        | zig       |
| Zig       | Yes        |   82.9 (50.7x)     |  310.9 (183.8x)    |    803 (18.3x)   |   32.7 (76.7x)    |   44.5 (103.1x)   | 0.7.1        | zig       |
| Rust      | No         |  300.2 (183.8x)    |  531.0 (313.9x)    |    237 (5.4x)    |   19.6 (46.1x)    |   33.5 (77.6x)    | 1.47.0       | rustc     |
| Rust      | Yes        |  276.8 (169.5x)    |  347.7 (205.5x)    |    224 (5.1x)    |   17.2 (40.4x)    |   23.4 (54.2x)    | 1.47.0       | rustc     |
| Nim       | No         |   36.3 (22.2x)     |  442.0 (261.3x)    |     68 (1.5x)    |    4.2 (9.8x)     |   31.8 (73.7x)    | 1.4.6        | nim       |
| C#        | No         |    N/A             |   25.0 (14.8x)     |    546 (12.5x)   |    N/A            |    4.7 (10.8x)    | 6.12.0.122   | mcs       |
| N/A       | N/A        |    N/A             |    N/A             |    N/A           |    N/A            |   11.9 (27.4x)    | N/A          | N/A       |
| N/A       | N/A        |    N/A             |    N/A             |    N/A           |    N/A            |   64.7 (149.9x)   | N/A          | N/A       |
| OCaml     | No         |    N/A             |  440.6 (260.5x)    |    216 (4.9x)    |    N/A            |   62.3 (144.4x)   | 4.08.1       | ocamlc    |
| Julia     | No         |    N/A             | 169629.6 (100280.5x) |    N/A           |    N/A            |  205.5 (476.0x)   | 1.7.0-DEV    | julia     |
| Julia     | Yes        |    N/A             | 130974.6 (77428.7x) |    N/A           |    N/A            |  162.8 (377.2x)   | 1.7.0-DEV    | julia     |

## TODO

- Sort table primarily by build time and then check time
- Don’t include Build Time and Build RSS columns when build op is not used.
- Don’t include Check Time and Check RSS columns when check op is not used.
- Add language Fortran.
- Add language Pony.

## References

- [Go compilation times compared to C++, D, Rust, Pascal (cross-posted)](https://www.reddit.com/r/golang/comments/55k7n4/go_compilation_times_compared_to_c_d_rust_pascal/)
- [LanguageCompilationSpeed](https://wiki.alopex.li/LanguageCompilationSpeed)
