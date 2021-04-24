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
- [Nim](https://nim-lang.org) (using `nim`),
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
| D         | Check      | No         | 6.0              | 4.6 [Vox]          | N/A               | v2.096.1-beta.1-187-gb25be89b3 | `dmd` |
| D         | Check      | No         | 7.5              | 5.7 [Vox]          | N/A               | 1.26.0-beta1 | `ldmd2` |
| D         | Check      | Yes        | 13.7             | 10.5 [Vox]         | N/A               | v2.096.1-beta.1-187-gb25be89b3 | `dmd` |
| D         | Check      | Yes        | 14.6             | 11.2 [Vox]         | N/A               | 1.26.0-beta1 | `ldmd2` |
| D         | Build      | No         | 51.0             | 29.8 [C]           | 43                | v2.096.1-beta.1-187-gb25be89b3 | `dmd` |
| D         | Build      | No         | 98.3             | 57.3 [C]           | 120               | 1.26.0-beta1 | `ldmd2` |
| D         | Build      | Yes        | 55.9             | 32.6 [C]           | 28                | v2.096.1-beta.1-187-gb25be89b3 | `dmd` |
| D         | Build      | Yes        | 108.5            | 63.2 [C]           | 153               | 1.26.0-beta1 | `ldmd2` |
| Vox       | Check      | No         | 1.3              | 1.0 [Vox]          | N/A               | master  | `vox` |
| Vox       | Check      | Yes        | 2.2              | 1.7 [Vox]          | N/A               | master  | `vox` |
| Vox       | Build      | No         | 5.3              | 3.1 [C]            | 31                | master  | `vox` |
| Vox       | Build      | Yes        | 5.7              | 3.3 [C]            | 23                | master  | `vox` |
| C         | Check      | No         | 1.6              | 1.2 [Vox]          | N/A               | 0.9.27  | `tcc` |
| C         | Check      | No         | 8.3              | 6.4 [Vox]          | N/A               | 9.3.0   | `gcc` |
| C         | Check      | No         | 8.2              | 6.3 [Vox]          | N/A               | 9.3.0   | `gcc-9` |
| C         | Check      | No         | 8.2              | 6.3 [Vox]          | N/A               | 10.2.0  | `gcc-10` |
| C         | Check      | No         | 14.6             | 11.2 [Vox]         | N/A               | 10.0.0  | `clang-10` |
| C         | Check      | No         | 15.4             | 11.8 [Vox]         | N/A               | 11.0.0-2~ubuntu20.04.1 | `clang-11` |
| C         | Build      | No         | 1.7              | 1.0 [C]            | 25                | 0.9.27  | `tcc` |
| C         | Build      | No         | 279.3            | 162.8 [C]          | 26                | 9.3.0   | `gcc` |
| C         | Build      | No         | 279.2            | 162.7 [C]          | 25                | 9.3.0   | `gcc-9` |
| C         | Build      | No         | 291.1            | 169.7 [C]          | 24                | 10.2.0  | `gcc-10` |
| C         | Build      | No         | 128.5            | 74.9 [C]           | 211               | 10.0.0  | `clang-10` |
| C         | Build      | No         | 126.2            | 73.6 [C]           | 172               | 11.0.0-2~ubuntu20.04.1 | `clang-11` |
| C++       | Check      | No         | 20.8             | 15.9 [Vox]         | N/A               | 9.3.0   | `g++` |
| C++       | Check      | No         | 19.9             | 15.2 [Vox]         | N/A               | 9.3.0   | `g++-9` |
| C++       | Check      | No         | 21.4             | 16.4 [Vox]         | N/A               | 10.2.0  | `g++-10` |
| C++       | Check      | No         | 21.2             | 16.2 [Vox]         | N/A               | 10.0.0  | `clang++-10` |
| C++       | Check      | No         | 21.8             | 16.7 [Vox]         | N/A               | 11.0.0-2~ubuntu20.04.1 | `clang++-11` |
| C++       | Check      | Yes        | 55.4             | 42.4 [Vox]         | N/A               | 9.3.0   | `g++` |
| C++       | Check      | Yes        | 56.0             | 42.9 [Vox]         | N/A               | 9.3.0   | `g++-9` |
| C++       | Check      | Yes        | 53.0             | 40.6 [Vox]         | N/A               | 10.2.0  | `g++-10` |
| C++       | Check      | Yes        | 33.8             | 25.9 [Vox]         | N/A               | 10.0.0  | `clang++-10` |
| C++       | Check      | Yes        | 35.4             | 27.1 [Vox]         | N/A               | 11.0.0-2~ubuntu20.04.1 | `clang++-11` |
| C++       | Build      | No         | 300.3            | 175.0 [C]          | 26                | 9.3.0   | `g++` |
| C++       | Build      | No         | 300.8            | 175.4 [C]          | 25                | 9.3.0   | `g++-9` |
| C++       | Build      | No         | 307.8            | 179.4 [C]          | 25                | 10.2.0  | `g++-10` |
| C++       | Build      | No         | 139.7            | 81.4 [C]           | 445               | 10.0.0  | `clang++-10` |
| C++       | Build      | No         | 139.1            | 81.1 [C]           | 185               | 11.0.0-2~ubuntu20.04.1 | `clang++-11` |
| C++       | Build      | Yes        | 389.3            | 226.9 [C]          | 26                | 9.3.0   | `g++` |
| C++       | Build      | Yes        | 391.9            | 228.4 [C]          | 26                | 9.3.0   | `g++-9` |
| C++       | Build      | Yes        | 395.9            | 230.8 [C]          | 27                | 10.2.0  | `g++-10` |
| C++       | Build      | Yes        | 211.2            | 123.1 [C]          | 177               | 10.0.0  | `clang++-10` |
| C++       | Build      | Yes        | 179.0            | 104.3 [C]          | 204               | 11.0.0-2~ubuntu20.04.1 | `clang++-11` |
| Ada       | Build      | No         | 1870.7           | 1090.5 [C]         | 32                | 10.2.0  | `gnat` |
| Ada       | Build      | No         | 1901.5           | 1108.4 [C]         | 45                | 10.2.0  | `gnat-10` |
| Go        | Check      | No         | 12.6             | 9.7 [Vox]          | N/A               | 1.16.3  | `gotype` |
| Go        | Build      | No         | 112.3            | 65.5 [C]           | 75                | 1.16.3  | `go` |
| Go        | Build      | No         | 451.0            | 262.9 [C]          | 28                | 10.2.0  | `gccgo-10` |
| Swift     | Check      | No         | 345.4            | 264.5 [Vox]        | N/A               | 5.3.3   | `swiftc` |
| Swift     | Build      | No         | 827.9            | 482.6 [C]          | 62                | 5.3.3   | `swiftc` |
| V         | Build      | No         | 18.2             | 10.6 [C]           | 225               | 0.2.2   | `v`  |
| V         | Build      | Yes        | 22.7             | 13.3 [C]           | 216               | 0.2.2   | `v`  |
| Zig       | Check      | No         | 60.2             | 46.1 [Vox]         | N/A               | 0.7.1   | `zig` |
| Zig       | Check      | Yes        | 82.9             | 63.5 [Vox]         | N/A               | 0.7.1   | `zig` |
| Rust      | Build      | No         | 544.6            | 317.4 [C]          | 75                | 1.47.0  | `rustc` |
| Rust      | Build      | Yes        | 362.4            | 211.2 [C]          | 117               | 1.47.0  | `rustc` |
| Nim       | Check      | No         | 35.3             | 27.1 [Vox]         | N/A               | 1.4.6   | `nim` |
| Nim       | Build      | No         | 1051.5           | 613.0 [C]          | 38                | 1.4.6   | `nim` |
| C#        | Build      | No         | 22.1             | 12.9 [C]           | 290               | 6.12.0.122 | `mcs` |
| Julia     | Build      | No         | 714206.9         | 416321.3 [C]       | N/A               | 1.7.0-DEV | `julia` |
| Julia     | Build      | Yes        | 565871.4         | 329854.4 [C]       | N/A               | 1.7.0-DEV | `julia` |

## TODO

- Merge columns
  - Op Time [us/#fn]
  - Slowdown vs [Best]
  into tuple (ABS, REL) with title
    Op Time [us/#fn]
- Fix Zig output file

/snap/bin/zig build-exe --name generated/zig/main generated/zig/main.zig
LLVM failed to emit file: No such file or directory

- Put check and build time in separate columns on same line
- Track memory usage of compilations using ideas at [Subprocess memory usage in python](https://stackoverflow.com/questions/13607391/subprocess-memory-usage-in-python/13607392).
- Parallelize calls to checkers and builders.
- Add language Fortran.
- Add language Pony.

## References

- [Go compilation times compared to C++, D, Rust, Pascal (cross-posted)](https://www.reddit.com/r/golang/comments/55k7n4/go_compilation_times_compared_to_c_d_rust_pascal/)
