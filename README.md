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
| D         | No         |    6.8  (minimum)    |  149.3 (11.6 tcc)    |    244 ( 1.4 gccgo-10) |    4.3 ( 1.6 tcc)        |   91.6 (31.5 tcc)        | v2.096.0     | dmd       |
| D         | No         |    7.4 ( 1.1 dmd)    |  867.1 (67.6 tcc)    |   1197 ( 6.8 gccgo-10) |    5.4 ( 2.0 tcc)        |  148.6 (51.1 tcc)        | 1.26.0-beta1 | ldmd2     |
| D         | No         |   52.1 ( 7.6 dmd)    | 2417.5 (188.5 tcc)   |    203 ( 1.1 gccgo-10) |   35.1 (12.8 tcc)        |  147.0 (50.6 tcc)        | 10.2.0       | gdc       |
| D         | Yes        |  109.7 (16.1 dmd)    |  221.4 (17.3 tcc)    |    341 ( 1.9 gccgo-10) |  105.1 (38.3 tcc)        |  165.1 (56.8 tcc)        | v2.096.0     | dmd       |
| D         | Yes        |  119.5 (17.5 dmd)    |  958.0 (74.7 tcc)    |   1105 ( 6.3 gccgo-10) |  117.3 (42.7 tcc)        |  226.0 (77.7 tcc)        | 1.26.0-beta1 | ldmd2     |
| Vox       | No         |   11.3 ( 1.7 dmd)    |   43.2 ( 3.4 tcc)    |    181 ( 1.0 gccgo-10) |    8.6 ( 3.1 tcc)        |   28.5 ( 9.8 tcc)        | master       | vox       |
| Vox       | Yes        |   19.2 ( 2.8 dmd)    |   46.2 ( 3.6 tcc)    |    221 ( 1.3 gccgo-10) |   15.7 ( 5.7 tcc)        |   34.2 (11.7 tcc)        | master       | vox       |
| C         | No         |   15.0 ( 2.2 dmd)    |   12.8  (minimum)    |    206 ( 1.2 gccgo-10) |    2.7  (minimum)        |    2.9  (minimum)        | 0.9.27       | tcc       |
| C         | No         |   64.5 ( 9.5 dmd)    | 2205.9 (172.0 tcc)   |    221 ( 1.3 gccgo-10) |   21.9 ( 8.0 tcc)        |  104.3 (35.9 tcc)        | 9.3.0        | gcc       |
| C         | No         |   69.7 (10.2 dmd)    | 2188.9 (170.7 tcc)   |    205 ( 1.2 gccgo-10) |   22.0 ( 8.0 tcc)        |  104.3 (35.9 tcc)        | 9.3.0        | gcc-9     |
| C         | No         |   67.4 ( 9.9 dmd)    | 2322.5 (181.1 tcc)   |    190 ( 1.1 gccgo-10) |   22.4 ( 8.2 tcc)        |  104.7 (36.0 tcc)        | 10.2.0       | gcc-10    |
| C         | No         |  115.5 (16.9 dmd)    |  995.1 (77.6 tcc)    |   1889 (10.7 gccgo-10) |   10.7 ( 3.9 tcc)        |   67.9 (23.3 tcc)        | 10.0.0-4ubuntu1 | clang-10  |
| C         | No         |  122.2 (17.9 dmd)    | 1008.3 (78.6 tcc)    |   1556 ( 8.8 gccgo-10) |   11.1 ( 4.0 tcc)        |   67.5 (23.2 tcc)        | 11.0.0-2 | clang-11  |
| C         | No         |   40.8 ( 6.0 dmd)    | not applicable       | not applicable     |   11.8 ( 4.3 tcc)        | not applicable           | unknown      | cproc     |
| C++       | No         |  161.9 (23.7 dmd)    | 2399.1 (187.1 tcc)   |    199 ( 1.1 gccgo-10) |   34.6 (12.6 tcc)        |  143.7 (49.4 tcc)        | 9.3.0        | g++       |
| C++       | No         |  164.0 (24.0 dmd)    | 2392.4 (186.6 tcc)   |    205 ( 1.2 gccgo-10) |   34.6 (12.6 tcc)        |  143.7 (49.4 tcc)        | 9.3.0        | g++-9     |
| C++       | No         |  163.5 (24.0 dmd)    | 2493.6 (194.5 tcc)   |    218 ( 1.2 gccgo-10) |   32.8 (11.9 tcc)        |  144.6 (49.7 tcc)        | 10.2.0       | g++-10    |
| C++       | No         |  167.0 (24.5 dmd)    | 1107.2 (86.3 tcc)    |   3631 (20.6 gccgo-10) |   11.4 ( 4.2 tcc)        |   68.7 (23.6 tcc)        | 10.0.0-4ubuntu1 | clang++-10 |
| C++       | No         |  169.5 (24.8 dmd)    | 1107.7 (86.4 tcc)    |   1524 ( 8.6 gccgo-10) |   11.8 ( 4.3 tcc)        |   68.7 (23.6 tcc)        | 11.0.0-2 | clang++-11 |
| C++       | Yes        |  455.3 (66.7 dmd)    | 3177.0 (247.8 tcc)   |    214 ( 1.2 gccgo-10) |   57.0 (20.8 tcc)        |  168.4 (57.9 tcc)        | 9.3.0        | g++       |
| C++       | Yes        |  445.0 (65.2 dmd)    | 3157.0 (246.2 tcc)   |    198 ( 1.1 gccgo-10) |   57.0 (20.8 tcc)        |  168.3 (57.9 tcc)        | 9.3.0        | g++-9     |
| C++       | Yes        |  470.0 (68.9 dmd)    | 3245.7 (253.1 tcc)   |    214 ( 1.2 gccgo-10) |   54.3 (19.8 tcc)        |  175.1 (60.2 tcc)        | 10.2.0       | g++-10    |
| C++       | Yes        |  273.6 (40.1 dmd)    | 1644.6 (128.3 tcc)   |   3841 (21.8 gccgo-10) |   25.9 ( 9.4 tcc)        |  105.6 (36.3 tcc)        | 10.0.0-4ubuntu1 | clang++-10 |
| C++       | Yes        |  283.7 (41.6 dmd)    | 1382.3 (107.8 tcc)   |   1411 ( 8.0 gccgo-10) |   26.5 ( 9.6 tcc)        |  106.2 (36.5 tcc)        | 11.0.0-2 | clang++-11 |
| Ada       | No         | not applicable       | 15276.9 (1191.4 tcc) |    391 ( 2.2 gccgo-10) | not applicable           |  250.1 (86.0 tcc)        | 10.2.0       | gnat      |
| Ada       | No         | not applicable       | 15271.1 (1191.0 tcc) |    345 ( 2.0 gccgo-10) | not applicable           |  250.2 (86.0 tcc)        | 10.2.0       | gnat-10   |
| Go        | No         |  109.5 (16.1 dmd)    | not applicable       | not applicable     |   28.3 (10.3 tcc)        | not applicable           | 1.16.3       | gotype    |
| Go        | No         | not applicable       |  897.4 (70.0 tcc)    |    375 ( 2.1 gccgo-10) | not applicable           |  213.0 (73.3 tcc)        | 1.16.3       | go        |
| Go        | No         | not applicable       | 3492.3 (272.4 tcc)   |    176  (minimum)  | not applicable           |  194.8 (67.0 tcc)        | 10.2.0       | gccgo-10  |
| Swift     | No         | 2728.9 (399.9 dmd)   | 6573.7 (512.7 tcc)   |    553 ( 3.1 gccgo-10) |   42.8 (15.6 tcc)        |  128.2 (44.1 tcc)        | 5.3.3        | swiftc    |
| V         | No         | not applicable       |  151.1 (11.8 tcc)    |   1880 (10.7 gccgo-10) | not applicable           |   92.6 (31.9 tcc)        | 0.2.2        | v         |
| V         | Yes        | not applicable       |  182.6 (14.2 tcc)    |   1673 ( 9.5 gccgo-10) | not applicable           |  102.8 (35.3 tcc)        | 0.2.2        | v         |
| Zig       | No         |  484.8 (71.0 dmd)    | not applicable       | not applicable     |  171.9 (62.6 tcc)        | not applicable           | 0.7.1        | zig       |
| Zig       | Yes        |  631.0 (92.5 dmd)    | not applicable       | not applicable     |  243.2 (88.6 tcc)        | not applicable           | 0.7.1        | zig       |
| Rust      | No         | not applicable       | 4302.7 (335.6 tcc)   |    901 ( 5.1 gccgo-10) | not applicable           |  257.8 (88.7 tcc)        | 1.47.0       | rustc     |
| Rust      | Yes        | not applicable       | 2917.8 (227.6 tcc)   |    932 ( 5.3 gccgo-10) | not applicable           |  180.8 (62.2 tcc)        | 1.47.0       | rustc     |
| Nim       | No         |  277.5 (40.7 dmd)    | 3559.7 (277.6 tcc)   |    274 ( 1.6 gccgo-10) |   31.3 (11.4 tcc)        |  253.7 (87.2 tcc)        | 1.4.6        | nim       |
| C#        | No         | not applicable       |  175.6 (13.7 tcc)    |   2480 (14.1 gccgo-10) | not applicable           |   29.8 (10.3 tcc)        | 6.12.0.122   | mcs       |
| Julia     | No         | not applicable       | 723116.5 (56395.7 tcc) | not applicable     | not applicable           |  333.7 (114.7 tcc)       | 1.7.0-DEV    | julia     |
| Julia     | Yes        | not applicable       | 551241.1 (42991.2 tcc) | not applicable     | not applicable           |  377.2 (129.7 tcc)       | 1.7.0-DEV    | julia     |

## TODO

- Fix Zig output file

/snap/bin/zig build-exe --name generated/zig/main generated/zig/main.zig
LLVM failed to emit file: No such file or directory

- Parallelize calls to checkers and builders.
- Add language Fortran.
- Add language Pony.

## References

- [Go compilation times compared to C++, D, Rust, Pascal (cross-posted)](https://www.reddit.com/r/golang/comments/55k7n4/go_compilation_times_compared_to_c_d_rust_pascal/)
