# compiler-benchmark

Benchmarks compilation speeds of different combinations of languages and
compilers. Supported languages are:

## Languages with Natives Compilers

- [C](https://en.wikipedia.org/wiki/C_(programming_language)) (using `gcc`),
- [C\+\+](http://www.cplusplus.org/) (using `g++`),
- [Ada](https://en.wikipedia.org/wiki/Ada_(programming_language)) (using `gnatgcc`),
- [D](https://dlang.org/) (using `dmd` `ldmd2`, and `gdc`),
- [Vox](https://github.com/MrSmith33/tiny_jit) (using `vox`),
- [Go](https://golang.org/) (using `go` or `gccgo`),
- [Rust](https://www.rust-lang.org/) (using `rustc`),
- [V](https://vlang.io/) (using `v`),
- [Zig](https://ziglang.org/) (using `zig`), and
- [Julia](https://julialang.org/) (using `julia`).

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

D's reference compiler `dmd` and Go's reference compiler `go` are still far
ahead of all its competition especially when it comes to default build (standard
compilation) performance. Further,

- Go's checker `gotype` is 2.5 times slower than D's builtin (`dmd -o-`) while
- D's `dmd` is 1.2 times slower on builds than Go's `go`

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

The output on my Intel® Core™ i7-4710HQ CPU @ 2.50GHz × 8 with 16 GB of memory
running Ubuntu 20.04 for the sample call

    ./benchmark --function-count=200 --function-depth=450 --run-count=3

or using [PyPy](https://www.pypy.org/) 3 (for faster code generation) as

    pypy3 ./benchmark --function-count=200 --function-depth=450 --run-count=3

results in the following table (copied from the output at the end).

| Lang-uage | Oper-ation | Temp-lated | Op Time [us/#fn] | Slowdown vs [Best] | Run Time [ns/#fn] | Version | Exec |
| :---: | :---: | --- | :---: | :---: | :---: | :---: | :---: |
| D | Check | No | 7.3 | 1.0 [D] | N/A | v2.093.1-657-g02c6484cb | `dmd` |
| D | Check | No | 7.8 | 1.1 [D] | N/A | 1.23.0 | `ldmd2` |
| D | Check | Yes | 18.6 | 2.5 [D] | N/A | v2.093.1-657-g02c6484cb | `dmd` |
| D | Check | Yes | 20.1 | 2.7 [D] | N/A | 1.23.0 | `ldmd2` |
| D | Build | No | 25.2 | 3.4 [Vox] | 82 | v2.093.1-657-g02c6484cb | `dmd` |
| D | Build | No | 200.4 | 27.2 [Vox] | 108 | 1.23.0 | `ldmd2` |
| D | Build | Yes | 38.5 | 5.2 [Vox] | 41 | v2.093.1-657-g02c6484cb | `dmd` |
| D | Build | Yes | 217.8 | 29.5 [Vox] | 42 | 1.23.0 | `ldmd2` |
| Vox | Build | No | 7.4 | 1.0 [Vox] | N/A | master | `vox` |
| Vox | Build | Yes | 8.2 | 1.1 [Vox] | N/A | master | `vox` |
| C | Check | No | 9.8 | 1.3 [D] | N/A | 8.4.0 | `gcc-8` |
| C | Check | No | 11.8 | 1.6 [D] | N/A | 9.3.0 | `gcc-9` |
| C | Check | No | 12.7 | 1.7 [D] | N/A | 10.2.0 | `gcc-10` |
| C | Check | No | 24.5 | 3.3 [D] | N/A | 8.0.1 | `clang-8` |
| C | Check | No | 26.7 | 3.6 [D] | N/A | 9.0.1 | `clang-9` |
| C | Check | No | 28.5 | 3.9 [D] | N/A | 10.0.0 | `clang-10` |
| C | Build | No | 371.3 | 50.4 [Vox] | 82 | 8.4.0 | `gcc-8` |
| C | Build | No | 413.1 | 56.0 [Vox] | 90 | 9.3.0 | `gcc-9` |
| C | Build | No | 430.2 | 58.4 [Vox] | 76 | 10.2.0 | `gcc-10` |
| C | Build | No | 170.6 | 23.1 [Vox] | 103 | 8.0.1 | `clang-8` |
| C | Build | No | 179.9 | 24.4 [Vox] | 108 | 9.0.1 | `clang-9` |
| C | Build | No | 178.5 | 24.2 [Vox] | 105 | 10.0.0 | `clang-10` |
| C++ | Check | No | 21.0 | 2.9 [D] | N/A | 8.4.0 | `g++-8` |
| C++ | Check | No | 33.6 | 4.6 [D] | N/A | 9.3.0 | `g++-9` |
| C++ | Check | No | 35.3 | 4.8 [D] | N/A | 10.2.0 | `g++-10` |
| C++ | Check | No | 34.6 | 4.7 [D] | N/A | 8.0.1 | `clang++-8` |
| C++ | Check | No | 36.5 | 5.0 [D] | N/A | 9.0.1 | `clang++-9` |
| C++ | Check | No | 39.3 | 5.4 [D] | N/A | 10.0.0 | `clang++-10` |
| C++ | Check | Yes | 57.8 | 7.9 [D] | N/A | 8.4.0 | `g++-8` |
| C++ | Check | Yes | 79.7 | 10.9 [D] | N/A | 9.3.0 | `g++-9` |
| C++ | Check | Yes | 82.6 | 11.3 [D] | N/A | 10.2.0 | `g++-10` |
| C++ | Check | Yes | 53.4 | 7.3 [D] | N/A | 8.0.1 | `clang++-8` |
| C++ | Check | Yes | 55.5 | 7.6 [D] | N/A | 9.0.1 | `clang++-9` |
| C++ | Check | Yes | 56.8 | 7.8 [D] | N/A | 10.0.0 | `clang++-10` |
| C++ | Build | No | 389.9 | 52.9 [Vox] | 81 | 8.4.0 | `g++-8` |
| C++ | Build | No | 442.8 | 60.1 [Vox] | 79 | 9.3.0 | `g++-9` |
| C++ | Build | No | 463.7 | 62.9 [Vox] | 75 | 10.2.0 | `g++-10` |
| C++ | Build | No | 183.9 | 25.0 [Vox] | 111 | 8.0.1 | `clang++-8` |
| C++ | Build | No | 194.2 | 26.3 [Vox] | 110 | 9.0.1 | `clang++-9` |
| C++ | Build | No | 191.2 | 25.9 [Vox] | 118 | 10.0.0 | `clang++-10` |
| C++ | Build | Yes | 8391.6 | 1138.3 [Vox] | 51 | 8.4.0 | `g++-8` |
| C++ | Build | Yes | 8197.4 | 1112.0 [Vox] | 51 | 9.3.0 | `g++-9` |
| C++ | Build | Yes | 8125.7 | 1102.3 [Vox] | 49 | 10.2.0 | `g++-10` |
| C++ | Build | Yes | 196.1 | 26.6 [Vox] | 51 | 8.0.1 | `clang++-8` |
| C++ | Build | Yes | 210.9 | 28.6 [Vox] | 56 | 9.0.1 | `clang++-9` |
| C++ | Build | Yes | 263.0 | 35.7 [Vox] | 56 | 10.0.0 | `clang++-10` |
| Ada | Build | No | 5164.8 | 700.6 [Vox] | N/A | 10.2.0 | `gnat-10` |
| Go | Check | No | 30.1 | 4.1 [D] | N/A | 8.4.0 | `gccgo-8` |
| Go | Check | No | 24.2 | 3.3 [D] | N/A | 9.3.0 | `gccgo-9` |
| Go | Build | No | 141.7 | 19.2 [Vox] | 43 | 1.15 | `go` |
| V | Build | No | 182.9 | 24.8 [Vox] | 45 | 0.1.29 | `v` |
| Zig | Check | No | 85.4 | 11.7 [D] | N/A | 0.6.0+32a77a604 | `zig` |
| Zig | Check | Yes | 111.8 | 15.2 [D] | N/A | 0.6.0+32a77a604 | `zig` |
| Zig | Build | No | 401.7 | 54.5 [Vox] | 71 | 0.6.0+32a77a604 | `zig` |
| Zig | Build | Yes | 430.7 | 58.4 [Vox] | 67 | 0.6.0+32a77a604 | `zig` |
| Rust | Check | No | 255.0 | 34.8 [D] | N/A | 1.48.0-nightly | `rustc` |
| Rust | Check | Yes | 271.0 | 37.0 [D] | N/A | 1.48.0-nightly | `rustc` |
| Rust | Build | No | 778.7 | 105.6 [Vox] | 120 | 1.46.0 | `rustc` |
| Rust | Build | No | 652.7 | 88.5 [Vox] | 121 | 1.48.0-nightly | `rustc` |
| Rust | Build | Yes | 486.3 | 66.0 [Vox] | 88 | 1.46.0 | `rustc` |
| Rust | Build | Yes | 429.9 | 58.3 [Vox] | 88 | 1.48.0-nightly | `rustc` |
| C# | Build | No | 26.1 | 3.5 [Vox] | 36766 | 6.8.0.105 | `mcs` |

This is with DMD built with LDC for an additional 15 percent drop in compilation time.

## TODO

- Put check and build time in separate columns on same line
- Track memory usage of compilations using ideas at [Subprocess memory usage in python](https://stackoverflow.com/questions/13607391/subprocess-memory-usage-in-python/13607392).
- Parallelize calls to checkers and builders.
- Add language Fortran.
- Add language Pony.

## References

- [Go compilation times compared to C++, D, Rust, Pascal (cross-posted)](https://www.reddit.com/r/golang/comments/55k7n4/go_compilation_times_compared_to_c_d_rust_pascal/)
