# compiler-benchmark

Benchmarks compilation speeds of different combinations of languages and
compilers. Supported languages are:

## Languages with Natives Compilers

- [C](https://en.wikipedia.org/wiki/C_(programming_language)) (using `gcc`, `clang` and [`cproc`](https://github.com/michaelforney/cproc),
- [C\+\+](http://www.cplusplus.org/) (using `g++` and `clang++`),
- [D](https://dlang.org/) (using `dmd` `ldmd2`, and `gdc`),
- [Go](https://golang.org/) (using `go` or `gccgo`),
- [Swift](https://swift.org/) (using `swiftc`),
- [Rust](https://www.rust-lang.org/) (using `rustc`),
- [Julia](https://julialang.org/) (using `julia`).
- [Ada](https://en.wikipedia.org/wiki/Ada_(programming_language)) (using `gnatgcc`),
- [Zig](https://ziglang.org/) (using `zig`), and
- [V](https://vlang.io/) (using `v`),
- [Vox](https://github.com/MrSmith33/tiny_jit) (using `vox`),

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

Vox, D's reference compiler `dmd` are far ahead of all its competition
especially when it comes to check and default build (standard compilation)
performance. Specifically,

- Vox's builds are, by a large margin, the fastest. 3.4 times faster than its
  closers competitor, `dmd`.
- D's `dmd` performs the fastest check. If and when Vox gets a separate check
  phase, it's likely gonna be signifcantly faster aswell because its build is
  only a couple of percent slower than `dmd`'s check.

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

| Lang-uage | Oper-ation | Temp-lated | Op Time [us/#fn] | Slowdown vs [Best] | Run Time [us/#fn] | Version | Exec |
| :---: | :---: | --- | :---: | :---: | :---: | :---: | :---: |
| D | Check | No | 6.7 | 1.0 [D] | N/A | v2.094.0-rc.1-75-ga0875a7e0 | `dmd` |
| D | Check | No | 7.9 | 1.2 [D] | N/A | 1.23.0 | `ldmd2` |
| D | Check | Yes | 17.8 | 2.6 [D] | N/A | v2.094.0-rc.1-75-ga0875a7e0 | `dmd` |
| D | Check | Yes | 19.7 | 2.9 [D] | N/A | 1.23.0 | `ldmd2` |
| D | Build | No | 23.8 | 3.4 [Vox] | 32 | v2.094.0-rc.1-75-ga0875a7e0 | `dmd` |
| D | Build | No | 190.6 | 27.5 [Vox] | 115 | 1.23.0 | `ldmd2` |
| D | Build | Yes | 36.6 | 5.3 [Vox] | 32 | v2.094.0-rc.1-75-ga0875a7e0 | `dmd` |
| D | Build | Yes | 207.8 | 30.0 [Vox] | 114 | 1.23.0 | `ldmd2` |
| Vox | Build | No | 6.9 | 1.0 [Vox] | N/A | master | `vox` |
| Vox | Build | Yes | 7.7 | 1.1 [Vox] | N/A | master | `vox` |
| C | Check | No | 10.4 | 1.5 [D] | N/A | 8.4.0 | `gcc-8` |
| C | Check | No | 12.4 | 1.8 [D] | N/A | 9.3.0 | `gcc-9` |
| C | Check | No | 13.5 | 2.0 [D] | N/A | 10.2.0 | `gcc-10` |
| C | Check | No | 25.1 | 3.7 [D] | N/A | 8.0.1 | `clang-8` |
| C | Check | No | 26.6 | 4.0 [D] | N/A | 9.0.1 | `clang-9` |
| C | Check | No | 27.3 | 4.1 [D] | N/A | 10.0.0 | `clang-10` |
| C | Check | No | 7.4 | 1.1 [D] | N/A | unknown | `cproc` |
| C | Build | No | 377.2 | 54.4 [Vox] | 19 | 8.4.0 | `gcc-8` |
| C | Build | No | 416.0 | 60.1 [Vox] | 22 | 9.3.0 | `gcc-9` |
| C | Build | No | 424.6 | 61.3 [Vox] | 19 | 10.2.0 | `gcc-10` |
| C | Build | No | 167.6 | 24.2 [Vox] | 367 | 8.0.1 | `clang-8` |
| C | Build | No | 173.5 | 25.1 [Vox] | 407 | 9.0.1 | `clang-9` |
| C | Build | No | 177.8 | 25.7 [Vox] | 421 | 10.0.0 | `clang-10` |
| C | Build | No | 63.7 | 9.2 [Vox] | 12 | unknown | `cproc` |
| C++ | Check | No | 20.3 | 3.0 [D] | N/A | 8.4.0 | `g++-8` |
| C++ | Check | No | 32.4 | 4.8 [D] | N/A | 9.3.0 | `g++-9` |
| C++ | Check | No | 33.9 | 5.1 [D] | N/A | 10.2.0 | `g++-10` |
| C++ | Check | No | 33.9 | 5.0 [D] | N/A | 8.0.1 | `clang++-8` |
| C++ | Check | No | 35.4 | 5.3 [D] | N/A | 9.0.1 | `clang++-9` |
| C++ | Check | No | 36.9 | 5.5 [D] | N/A | 10.0.0 | `clang++-10` |
| C++ | Check | Yes | 58.2 | 8.7 [D] | N/A | 8.4.0 | `g++-8` |
| C++ | Check | Yes | 74.6 | 11.1 [D] | N/A | 9.3.0 | `g++-9` |
| C++ | Check | Yes | 80.5 | 12.0 [D] | N/A | 10.2.0 | `g++-10` |
| C++ | Check | Yes | 51.5 | 7.7 [D] | N/A | 8.0.1 | `clang++-8` |
| C++ | Check | Yes | 54.7 | 8.2 [D] | N/A | 9.0.1 | `clang++-9` |
| C++ | Check | Yes | 56.7 | 8.4 [D] | N/A | 10.0.0 | `clang++-10` |
| C++ | Build | No | 378.8 | 54.7 [Vox] | 19 | 8.4.0 | `g++-8` |
| C++ | Build | No | 431.9 | 62.3 [Vox] | 25 | 9.3.0 | `g++-9` |
| C++ | Build | No | 443.2 | 64.0 [Vox] | 18 | 10.2.0 | `g++-10` |
| C++ | Build | No | 172.8 | 24.9 [Vox] | 400 | 8.0.1 | `clang++-8` |
| C++ | Build | No | 183.3 | 26.5 [Vox] | 425 | 9.0.1 | `clang++-9` |
| C++ | Build | No | 187.6 | 27.1 [Vox] | 410 | 10.0.0 | `clang++-10` |
| C++ | Build | Yes | 8226.6 | 1187.5 [Vox] | 25 | 8.4.0 | `g++-8` |
| C++ | Build | Yes | 8571.2 | 1237.3 [Vox] | 21 | 9.3.0 | `g++-9` |
| C++ | Build | Yes | 8469.7 | 1222.6 [Vox] | 24 | 10.2.0 | `g++-10` |
| C++ | Build | Yes | 202.2 | 29.2 [Vox] | 419 | 8.0.1 | `clang++-8` |
| C++ | Build | Yes | 211.1 | 30.5 [Vox] | 452 | 9.0.1 | `clang++-9` |
| C++ | Build | Yes | 279.5 | 40.3 [Vox] | 418 | 10.0.0 | `clang++-10` |
| Ada | Build | No | 5746.1 | 829.5 [Vox] | N/A | 10.2.0 | `gnat-10` |
| Go | Check | No | 35.7 | 5.3 [D] | N/A | 8.4.0 | `gccgo-8` |
| Go | Check | No | 28.3 | 4.2 [D] | N/A | 9.3.0 | `gccgo-9` |
| Go | Build | No | 170.8 | 24.7 [Vox] | 116 | 1.15.2 | `go` |
| Swift | Check | No | 477.3 | 71.1 [D] | N/A | 5.3 | `swiftc` |
| Swift | Build | No | 1108.8 | 160.1 [Vox] | 78 | 5.3 | `swiftc` |
| V | Build | No | 186.7 | 27.0 [Vox] | 31 | 0.1.29 | `v` |
| Zig | Check | No | 113.6 | 16.9 [D] | N/A | 0.6.0+a50260470 | `zig` |
| Zig | Check | Yes | 110.5 | 16.5 [D] | N/A | 0.6.0+a50260470 | `zig` |
| Zig | Build | No | 438.8 | 63.3 [Vox] | 384 | 0.6.0+a50260470 | `zig` |
| Zig | Build | Yes | 437.3 | 63.1 [Vox] | 390 | 0.6.0+a50260470 | `zig` |
| Rust | Check | No | 265.0 | 39.5 [D] | N/A | 1.48.0-nightly | `rustc` |
| Rust | Check | Yes | 285.5 | 42.5 [D] | N/A | 1.48.0-nightly | `rustc` |
| Rust | Build | No | 787.9 | 113.7 [Vox] | 409 | 1.46.0 | `rustc` |
| Rust | Build | No | 660.4 | 95.3 [Vox] | 200 | 1.48.0-nightly | `rustc` |
| Rust | Build | Yes | 486.8 | 70.3 [Vox] | 424 | 1.46.0 | `rustc` |
| Rust | Build | Yes | 438.4 | 63.3 [Vox] | 198 | 1.48.0-nightly | `rustc` |
| C# | Build | No | 27.4 | 4.0 [Vox] | 262 | 6.8.0.105 | `mcs` |

This is with DMD built with LDC for an additional 15 percent drop in compilation time.

## TODO

- Put check and build time in separate columns on same line
- Track memory usage of compilations using ideas at [Subprocess memory usage in python](https://stackoverflow.com/questions/13607391/subprocess-memory-usage-in-python/13607392).
- Parallelize calls to checkers and builders.
- Add language Fortran.
- Add language Pony.

## References

- [Go compilation times compared to C++, D, Rust, Pascal (cross-posted)](https://www.reddit.com/r/golang/comments/55k7n4/go_compilation_times_compared_to_c_d_rust_pascal/)
