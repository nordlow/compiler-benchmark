# compiler-benchmark

Benchmarks compilation speeds of different combinations of languages and
compilers. Supported languages are:

## Languages with Natives Compilers

- C (using `gcc`),
- C++ (using `g++`),
- Ada (using `gnatgcc`),
- D (using `dmd` `ldmd2`, and `gdc`),
- Go (using `go` or `gccgo`),
- Rust (using `rustc`),
- V (using `v`),
- Zig (using `zig`), and
- Julia (using `julia`).

## Languages with Bytecode Compilers:

- OCaml (using `ocamlopt`),
- C# (using `mcs`), and
- Java (using `javac`).

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

The numerical constants are randomize using a new seed upon every call. This
makes it impossible for any compiler to utilize any caching mechanism upon
successive calls with same flags that affect the source generation. The purpose
of this is to make the comparison between compilers with different levels of
caching more fair.

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

| Lang-uage | Oper-ation | Temp-lated | Time [us/#fn] | Slowdown vs [Best] | Version | Exec |
| :---: | :---: | --- | :---: | :---: | :---: | :---: |
| D | Check | No | 0.610 | 1.0 [D] | v2.093.1-399-g4d2ee79c7 | `dmd` |
| D | Check | No | 0.683 | 1.1 [D] | 1.23.0 | `ldmd2` |
| D | Check | Yes | 1.491 | 2.4 [D] | v2.093.1-399-g4d2ee79c7 | `dmd` |
| D | Check | Yes | 1.642 | 2.7 [D] | 1.23.0 | `ldmd2` |
| D | Build | No | 1.509 | 1.2 [Go] | v2.093.1-399-g4d2ee79c7 | `dmd` |
| D | Build | No | 17.022 | 13.9 [Go] | 1.23.0 | `ldmd2` |
| D | Build | Yes | 2.627 | 2.1 [Go] | v2.093.1-399-g4d2ee79c7 | `dmd` |
| D | Build | Yes | 18.559 | 15.2 [Go] | 1.23.0 | `ldmd2` |
| C | Check | No | 0.815 | 1.3 [D] | 8.4.0 | `gcc-8` |
| C | Check | No | 1.075 | 1.8 [D] | 9.3.0 | `gcc-9` |
| C | Check | No | 1.213 | 2.0 [D] | 10.2.0 | `gcc-10` |
| C | Check | No | 2.277 | 3.7 [D] | 8.0.1 | `clang-8` |
| C | Check | No | 2.476 | 4.1 [D] | 9.0.1 | `clang-9` |
| C | Check | No | 2.680 | 4.4 [D] | 10.0.0 | `clang-10` |
| C | Build | No | 32.603 | 26.7 [Go] | 8.4.0 | `gcc-8` |
| C | Build | No | 36.307 | 29.7 [Go] | 9.3.0 | `gcc-9` |
| C | Build | No | 38.210 | 31.3 [Go] | 10.2.0 | `gcc-10` |
| C | Build | No | 15.469 | 12.7 [Go] | 8.0.1 | `clang-8` |
| C | Build | No | 16.224 | 13.3 [Go] | 9.0.1 | `clang-9` |
| C | Build | No | 16.835 | 13.8 [Go] | 10.0.0 | `clang-10` |
| C++ | Check | No | 1.819 | 3.0 [D] | 8.4.0 | `g++-8` |
| C++ | Check | No | 2.980 | 4.9 [D] | 9.3.0 | `g++-9` |
| C++ | Check | No | 3.094 | 5.1 [D] | 10.2.0 | `g++-10` |
| C++ | Check | No | 3.166 | 5.2 [D] | 8.0.1 | `clang++-8` |
| C++ | Check | No | 3.717 | 6.1 [D] | 9.0.1 | `clang++-9` |
| C++ | Check | No | 3.516 | 5.8 [D] | 10.0.0 | `clang++-10` |
| C++ | Check | Yes | 5.438 | 8.9 [D] | 8.4.0 | `g++-8` |
| C++ | Check | Yes | 6.901 | 11.3 [D] | 9.3.0 | `g++-9` |
| C++ | Check | Yes | 7.505 | 12.3 [D] | 10.2.0 | `g++-10` |
| C++ | Check | Yes | 4.973 | 8.2 [D] | 8.0.1 | `clang++-8` |
| C++ | Check | Yes | 5.370 | 8.8 [D] | 9.0.1 | `clang++-9` |
| C++ | Check | Yes | 5.518 | 9.0 [D] | 10.0.0 | `clang++-10` |
| C++ | Build | No | 35.732 | 29.2 [Go] | 8.4.0 | `g++-8` |
| C++ | Build | No | 39.840 | 32.6 [Go] | 9.3.0 | `g++-9` |
| C++ | Build | No | 41.310 | 33.8 [Go] | 10.2.0 | `g++-10` |
| C++ | Build | No | 15.924 | 13.0 [Go] | 8.0.1 | `clang++-8` |
| C++ | Build | No | 17.004 | 13.9 [Go] | 9.0.1 | `clang++-9` |
| C++ | Build | No | 17.256 | 14.1 [Go] | 10.0.0 | `clang++-10` |
| C++ | Build | Yes | 761.314 | 623.1 [Go] | 8.4.0 | `g++-8` |
| C++ | Build | Yes | 742.962 | 608.0 [Go] | 9.3.0 | `g++-9` |
| C++ | Build | Yes | 801.357 | 655.8 [Go] | 10.2.0 | `g++-10` |
| C++ | Build | Yes | 17.591 | 14.4 [Go] | 8.0.1 | `clang++-8` |
| C++ | Build | Yes | 17.990 | 14.7 [Go] | 9.0.1 | `clang++-9` |
| C++ | Build | Yes | 24.632 | 20.2 [Go] | 10.0.0 | `clang++-10` |
| Ada | Build | No | 504.430 | 412.8 [Go] | 10.2.0 | `gnat-10` |
| Go | Check | No | 1.610 | 2.6 [D] | 1.15 | `gotype` |
| Go | Check | No | 2.230 | 3.7 [D] | 9.3.0 | `gccgo-9` |
| Go | Check | No | 2.259 | 3.7 [D] | 10.2.0 | `gccgo-10` |
| Go | Build | No | 1.222 | 1.0 [Go] | 1.15 | `go` |
| Go | Build | No | 2.952 | 2.4 [Go] | 9.3.0 | `gccgo-9` |
| Go | Build | No | 3.161 | 2.6 [Go] | 10.2.0 | `gccgo-10` |
| V | Build | No | 16.520 | 13.5 [Go] | 0.1.29 | `v` |
| Zig | Check | No | 10.459 | 17.1 [D] | 0.6.0+4e63cae36 | `zig` |
| Zig | Check | Yes | 10.151 | 16.6 [D] | 0.6.0+4e63cae36 | `zig` |
| Rust | Check | No | 38.084 | 62.4 [D] | 1.45.2 | `rustc` |
| Rust | Check | No | 23.585 | 38.7 [D] | 1.47.0-nightly | `rustc` |
| Rust | Check | Yes | 35.203 | 57.7 [D] | 1.45.2 | `rustc` |
| Rust | Check | Yes | 25.275 | 41.4 [D] | 1.47.0-nightly | `rustc` |
| Rust | Build | No | 73.393 | 60.1 [Go] | 1.45.2 | `rustc` |
| Rust | Build | No | 76.754 | 62.8 [Go] | 1.47.0-nightly | `rustc` |
| Rust | Build | Yes | 45.864 | 37.5 [Go] | 1.45.2 | `rustc` |
| Rust | Build | Yes | 46.673 | 38.2 [Go] | 1.47.0-nightly | `rustc` |
| C# | Build | No | 2.287 | 1.9 [Go] | 6.8.0.105 | `mcs` |
| Java | Build | No | 9.023 | 7.4 [Go] | 1.8.0_171 | `javac` |
| OCaml | Build | No | 6.684 | 5.5 [Go] | 4.08.1 | `ocamlc` |

This is with DMD built with LDC for an additional 15 percent drop in compilation time.

## TODO

- Put check and build time in separate columns on same line
- Measure link and run-time and add to columns
- Track memory usage of compilations using ideas at [Subprocess memory usage in python](https://stackoverflow.com/questions/13607391/subprocess-memory-usage-in-python/13607392).
- Parallelize calls to checkers and builders.
- Add language Fortran.

## References

- [Go compilation times compared to C++, D, Rust, Pascal (cross-posted)](https://www.reddit.com/r/golang/comments/55k7n4/go_compilation_times_compared_to_c_d_rust_pascal/)
