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

    ./benchmark --function-count=200 --function-depth=400 --run-count=1

results in the following table (copied from the output at the end).

| Lang-uage | Temp-lated | Check Time [us/func] | Build Time [us/func] | Run Time [us/func] | Check Peak RSS [kB/func] | Build Peak RSS [kB/func] | Exec Version | Exec Path |
| :-------: | ---------- | :------------------: | :------------------: | :----------------: | :----------------------: | :----------------------: | :----------: | :-------: |
| D         | No         |    6.8  (best)    |  149.3 (11.6x)    |    244 (1.4x) |    4.3 (1.6x)        |   91.6 (31.5x)        | v2.096.0     |x       |
| D         | No         |    7.4 (1.1x)    |  867.1 (67.6x)    |   1197 (6.8x) |    5.4 (2.0x)        |  148.6 (51.1x)        | 1.26.0-beta1 | ldmd2     |
| D         | No         |   52.1 (7.6x)    | 2417.5 (188.5x)   |    203 (1.1x) |   35.1 (12.8x)        |  147.0 (50.6x)        | 10.2.0       | gdc       |
| D         | Yes        |  109.7 (16.1x)    |  221.4 (17.3x)    |    341 (1.9x) |  105.1 (38.3x)        |  165.1 (56.8x)        | v2.096.0     |x       |
| D         | Yes        |  119.5 (17.5x)    |  958.0 (74.7x)    |   1105 (6.3x) |  117.3 (42.7x)        |  226.0 (77.7x)        | 1.26.0-beta1 | ldmd2     |
| Vox       | No         |   11.3 (1.7x)    |   43.2 (3.4x)    |    181 (1.0x) |    8.6 (3.1x)        |   28.5 (9.8x)        | master       | vox       |
| Vox       | Yes        |   19.2 (2.8x)    |   46.2 (3.6x)    |    221 (1.3x) |   15.7 (5.7x)        |   34.2 (11.7x)        | master       | vox       |
| C         | No         |   15.0 (2.2x)    |   12.8  (best)    |    206 (1.2x) |    2.7  (best)        |    2.9  (best)        | 0.9.27       | tcc       |
| C         | No         |   64.5 (9.5x)    | 2205.9 (172.0x)   |    221 (1.3x) |   21.9 (8.0x)        |  104.3 (35.9x)        | 9.3.0        | gcc       |
| C         | No         |   69.7 (10.2x)    | 2188.9 (170.7x)   |    205 (1.2x) |   22.0 (8.0x)        |  104.3 (35.9x)        | 9.3.0        | gcc-9     |
| C         | No         |   67.4 (9.9x)    | 2322.5 (181.1x)   |    190 (1.1x) |   22.4 (8.2x)        |  104.7 (36.0x)        | 10.2.0       | gcc-10    |
| C         | No         |  115.5 (16.9x)    |  995.1 (77.6x)    |   1889 (10.7x) |   10.7 (3.9x)        |   67.9 (23.3x)        | 10.0.0 | clang-10  |
| C         | No         |  122.2 (17.9x)    | 1008.3 (78.6x)    |   1556 (8.8x) |   11.1 (4.0x)        |   67.5 (23.2x)        | 11.0.0-2 | clang-11  |
| C         | No         |   40.8 (6.0x)    | N/A       | N/A     |   11.8 (4.3x)        | N/A           | unknown      | cproc     |
| C++       | No         |  161.9 (23.7x)    | 2399.1 (187.1x)   |    199 (1.1x) |   34.6 (12.6x)        |  143.7 (49.4x)        | 9.3.0        | g++       |
| C++       | No         |  164.0 (24.0x)    | 2392.4 (186.6x)   |    205 (1.2x) |   34.6 (12.6x)        |  143.7 (49.4x)        | 9.3.0        | g++-9     |
| C++       | No         |  163.5 (24.0x)    | 2493.6 (194.5x)   |    218 (1.2x) |   32.8 (11.9x)        |  144.6 (49.7x)        | 10.2.0       | g++-10    |
| C++       | No         |  167.0 (24.5x)    | 1107.2 (86.3x)    |   3631 (20.6x) |   11.4 (4.2x)        |   68.7 (23.6x)        | 10.0.0 | clang++-10 |
| C++       | No         |  169.5 (24.8x)    | 1107.7 (86.4x)    |   1524 (8.6x) |   11.8 (4.3x)        |   68.7 (23.6x)        | 11.0.0-2 | clang++-11 |
| C++       | Yes        |  455.3 (66.7x)    | 3177.0 (247.8x)   |    214 (1.2x) |   57.0 (20.8x)        |  168.4 (57.9x)        | 9.3.0        | g++       |
| C++       | Yes        |  445.0 (65.2x)    | 3157.0 (246.2x)   |    198 (1.1x) |   57.0 (20.8x)        |  168.3 (57.9x)        | 9.3.0        | g++-9     |
| C++       | Yes        |  470.0 (68.9x)    | 3245.7 (253.1x)   |    214 (1.2x) |   54.3 (19.8x)        |  175.1 (60.2x)        | 10.2.0       | g++-10    |
| C++       | Yes        |  273.6 (40.1x)    | 1644.6 (128.3x)   |   3841 (21.8x) |   25.9 (9.4x)        |  105.6 (36.3x)        | 10.0.0 | clang++-10 |
| C++       | Yes        |  283.7 (41.6x)    | 1382.3 (107.8x)   |   1411 (8.0x) |   26.5 (9.6x)        |  106.2 (36.5x)        | 11.0.0-2 | clang++-11 |
| Ada       | No         | N/A       | 15276.9 (1191.4x) |    391 (2.2x) | N/A           |  250.1 (86.0x)        | 10.2.0       | gnat      |
| Ada       | No         | N/A       | 15271.1 (1191.0x) |    345 (2.0x) | N/A           |  250.2 (86.0x)        | 10.2.0       | gnat-10   |
| Go        | No         |  109.5 (16.1x)    | N/A       | N/A     |   28.3 (10.3x)        | N/A           | 1.16.3       | gotype    |
| Go        | No         | N/A       |  897.4 (70.0x)    |    375 (2.1x) | N/A           |  213.0 (73.3x)        | 1.16.3       | go        |
| Go        | No         | N/A       | 3492.3 (272.4x)   |    176  (best)  | N/A           |  194.8 (67.0x)        | 10.2.0       | gccgo-10  |
| Swift     | No         | 2728.9 (399.9x)   | 6573.7 (512.7x)   |    553 (3.1x) |   42.8 (15.6x)        |  128.2 (44.1x)        | 5.3.3        | swiftc    |
| V         | No         | N/A       |  151.1 (11.8x)    |   1880 (10.7x) | N/A           |   92.6 (31.9x)        | 0.2.2        | v         |
| V         | Yes        | N/A       |  182.6 (14.2x)    |   1673 (9.5x) | N/A           |  102.8 (35.3x)        | 0.2.2        | v         |
| Zig       | No         |  484.8 (71.0x)    | N/A       | N/A     |  171.9 (62.6x)        | N/A           | 0.7.1        | zig       |
| Zig       | Yes        |  631.0 (92.5x)    | N/A       | N/A     |  243.2 (88.6x)        | N/A           | 0.7.1        | zig       |
| Rust      | No         | N/A       | 4302.7 (335.6x)   |    901 (5.1x) | N/A           |  257.8 (88.7x)        | 1.47.0       | rustc     |
| Rust      | Yes        | N/A       | 2917.8 (227.6x)   |    932 (5.3x) | N/A           |  180.8 (62.2x)        | 1.47.0       | rustc     |
| Nim       | No         |  277.5 (40.7x)    | 3559.7 (277.6x)   |    274 (1.6x) |   31.3 (11.4x)        |  253.7 (87.2x)        | 1.4.6        | nim       |
| C#        | No         | N/A       |  175.6 (13.7x)    |   2480 (14.1x) | N/A           |   29.8 (10.3x)        | 6.12.0.122   | mcs       |
| Julia     | No         | N/A       | 723116.5 (56395.7x) | N/A     | N/A           |  333.7 (114.7x)       | 1.7.0-DEV    | julia     |
| Julia     | Yes        | N/A       | 551241.1 (42991.2x) | N/A     | N/A           |  377.2 (129.7x)       | 1.7.0-DEV    | julia     |

## TODO

- Fix Zig output file

/snap/bin/zig build-exe --name generated/zig/main generated/zig/main.zig
LLVM failed to emit file: No such file or directory

- Parallelize calls to checkers and builders.
- Add language Fortran.
- Add language Pony.

## References

- [Go compilation times compared to C++, D, Rust, Pascal (cross-posted)](https://www.reddit.com/r/golang/comments/55k7n4/go_compilation_times_compared_to_c_d_rust_pascal/)
