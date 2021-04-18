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
- [Julia](https://julialang.org/) (using `julia`).
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

Vox's check and build are, by a large margin, the fastest. 3-4 times faster than
its closers competitor, `dmd`. Note that Vox, however, is a highly experimental
language with no official release status, a Windows-only backend, and less
language features than most other languages benchmarked.

In second place comes D's reference compiler `dmd` and `cproc`. However, note
that `cproc` is a highly experimental C compiler with no builtin support for the
C preprocessor.

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

| Lang-uage | Oper-ation | Temp-lated | Op Time [us/#fn] | Slowdown vs [Best] | Run Time [us/#fn] | Version | Exec |
| :-------: | :--------: | ---------- | :--------------: | :----------------: | :---------------: | :-----: | :--: |
| D         | Check      | No         | 6.5              | 5.5 [Vox]          | N/A               | v2.096.1-beta.1-183-g640bc3abf | `dmd` |
| D         | Check      | No         | 7.5              | 6.3 [Vox]          | N/A               | 1.26.0-beta1 | `ldmd2` |
| D         | Check      | Yes        | 13.8             | 11.5 [Vox]         | N/A               | v2.096.1-beta.1-183-g640bc3abf | `dmd` |
| D         | Check      | Yes        | 15.7             | 13.1 [Vox]         | N/A               | 1.26.0-beta1 | `ldmd2` |
| D         | Build      | No         | 48.6             | 30.7 [C]           | 41                | v2.096.1-beta.1-183-g640bc3abf | `dmd` |
| D         | Build      | No         | 99.9             | 63.2 [C]           | 136               | 1.26.0-beta1 | `ldmd2` |
| D         | Build      | Yes        | 58.5             | 37.1 [C]           | 36                | v2.096.1-beta.1-183-g640bc3abf | `dmd` |
| D         | Build      | Yes        | 108.1            | 68.5 [C]           | 151               | 1.26.0-beta1 | `ldmd2` |
| Vox       | Check      | No         | 1.2              | 1.0 [Vox]          | N/A               | master  | `vox` |
| Vox       | Check      | Yes        | 2.0              | 1.7 [Vox]          | N/A               | master  | `vox` |
| Vox       | Build      | No         | 5.1              | 3.3 [C]            | N/A               | master  | `vox` |
| Vox       | Build      | Yes        | 5.6              | 3.6 [C]            | N/A               | master  | `vox` |
| C         | Check      | No         | 1.6              | 1.3 [Vox]          | N/A               | 0.9.27  | `tcc` |
| C         | Check      | No         | 8.5              | 7.1 [Vox]          | N/A               | 9.3.0   | `gcc` |
| C         | Check      | No         | 8.4              | 7.0 [Vox]          | N/A               | 9.3.0   | `gcc-9` |
| C         | Check      | No         | 8.5              | 7.1 [Vox]          | N/A               | 10.2.0  | `gcc-10` |
| C         | Check      | No         | 15.8             | 13.2 [Vox]         | N/A               | 10.0.0  | `clang-10` |
| C         | Build      | No         | 1.6              | 1.0 [C]            | 22                | 0.9.27  | `tcc` |
| C         | Build      | No         | 283.8            | 179.7 [C]          | 27                | 9.3.0   | `gcc` |
| C         | Build      | No         | 287.8            | 182.2 [C]          | 30                | 9.3.0   | `gcc-9` |
| C         | Build      | No         | 294.3            | 186.3 [C]          | 25                | 10.2.0  | `gcc-10` |
| C         | Build      | No         | 132.3            | 83.8 [C]           | 200               | 10.0.0  | `clang-10` |
| C++       | Check      | No         | 20.2             | 16.9 [Vox]         | N/A               | 9.3.0   | `g++` |
| C++       | Check      | No         | 20.4             | 17.0 [Vox]         | N/A               | 9.3.0   | `g++-9` |
| C++       | Check      | No         | 22.3             | 18.6 [Vox]         | N/A               | 10.2.0  | `g++-10` |
| C++       | Check      | No         | 21.0             | 17.5 [Vox]         | N/A               | 10.0.0  | `clang++-10` |
| C++       | Check      | Yes        | 57.5             | 47.9 [Vox]         | N/A               | 9.3.0   | `g++` |
| C++       | Check      | Yes        | 53.8             | 44.8 [Vox]         | N/A               | 9.3.0   | `g++-9` |
| C++       | Check      | Yes        | 54.8             | 45.7 [Vox]         | N/A               | 10.2.0  | `g++-10` |
| C++       | Check      | Yes        | 34.8             | 29.0 [Vox]         | N/A               | 10.0.0  | `clang++-10` |
| C++       | Build      | No         | 301.1            | 190.6 [C]          | 27                | 9.3.0   | `g++` |
| C++       | Build      | No         | 304.0            | 192.5 [C]          | 25                | 9.3.0   | `g++-9` |
| C++       | Build      | No         | 319.0            | 202.0 [C]          | 26                | 10.2.0  | `g++-10` |
| C++       | Build      | No         | 137.8            | 87.2 [C]           | 199               | 10.0.0  | `clang++-10` |
| C++       | Build      | Yes        | 392.0            | 248.2 [C]          | 26                | 9.3.0   | `g++` |
| C++       | Build      | Yes        | 388.3            | 245.8 [C]          | 26                | 9.3.0   | `g++-9` |
| C++       | Build      | Yes        | 404.4            | 256.0 [C]          | 25                | 10.2.0  | `g++-10` |
| C++       | Build      | Yes        | 213.8            | 135.3 [C]          | 474               | 10.0.0  | `clang++-10` |
| Ada       | Build      | No         | 1898.1           | 1201.8 [C]         | 43                | 10.2.0  | `gnat` |
| Ada       | Build      | No         | 1904.4           | 1205.8 [C]         | 45                | 10.2.0  | `gnat-10` |
| Go        | Check      | No         | 12.8             | 10.7 [Vox]         | N/A               | 1.16.3  | `gotype` |
| Go        | Build      | No         | 115.0            | 72.8 [C]           | 65                | 1.16.3  | `go` |
| Go        | Build      | No         | 450.7            | 285.4 [C]          | 24                | 10.2.0  | `gccgo-10` |
| Swift     | Check      | No         | 343.9            | 286.7 [Vox]        | N/A               | 5.3.3   | `swiftc` |
| Swift     | Build      | No         | 822.4            | 520.7 [C]          | 77                | 5.3.3   | `swiftc` |
| V         | Build      | No         | 18.2             | 11.5 [C]           | 188               | 0.2.2   | `v`  |
| V         | Build      | Yes        | 22.0             | 13.9 [C]           | 189               | 0.2.2   | `v`  |
| Zig       | Check      | No         | 63.1             | 52.6 [Vox]         | N/A               | 0.7.1   | `zig` |
| Zig       | Check      | Yes        | 80.4             | 67.0 [Vox]         | N/A               | 0.7.1   | `zig` |
| Rust      | Build      | No         | 547.1            | 346.4 [C]          | 75                | 1.47.0  | `rustc` |
| Rust      | Build      | Yes        | 369.6            | 234.0 [C]          | 74                | 1.47.0  | `rustc` |
| Nim       | Check      | No         | 35.1             | 29.3 [Vox]         | N/A               | 1.4.6   | `nim` |
| Nim       | Build      | No         | 1051.3           | 665.6 [C]          | 50                | 1.4.6   | `nim` |
| C#        | Build      | No         | 22.3             | 14.1 [C]           | 284               | 6.12.0.122 | `mcs` |
| Julia     | Build      | No         | 719209.5         | 455354.5 [C]       | N/A               | 1.7.0-DEV | `julia` |
| Julia     | Build      | Yes        | 560722.7         | 355011.5 [C]       | N/A               | 1.7.0-DEV | `julia` |

## TODO

- Put check and build time in separate columns on same line
- Track memory usage of compilations using ideas at [Subprocess memory usage in python](https://stackoverflow.com/questions/13607391/subprocess-memory-usage-in-python/13607392).
- Parallelize calls to checkers and builders.
- Add language Fortran.
- Add language Pony.

## References

- [Go compilation times compared to C++, D, Rust, Pascal (cross-posted)](https://www.reddit.com/r/golang/comments/55k7n4/go_compilation_times_compared_to_c_d_rust_pascal/)
