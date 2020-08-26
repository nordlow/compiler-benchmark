# compiler-benchmark

Benchmarks compilation speeds of different combinations of languages and
compilers. Supported languages are:

## Languages with Natives Compilers

- C (using `gcc`),
- C++ (using `g++`),
- Ada (using `gnatgcc`),
- D (using `dmd` `ldmd2`, and `gdc`),
- Vox (using `vox`),
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
| D | Check | No | 7.1 | 1.0 [D] | v2.093.1-401-g164ef8f01 | `dmd` |
| D | Check | No | 8.6 | 1.2 [D] | 1.23.0 | `ldmd2` |
| D | Check | Yes | 18.8 | 2.7 [D] | v2.093.1-401-g164ef8f01 | `dmd` |
| D | Check | Yes | 20.6 | 2.9 [D] | 1.23.0 | `ldmd2` |
| D | Build | No | 17.6 | 1.3 [Go] | v2.093.1-401-g164ef8f01 | `dmd` |
| D | Build | No | 199.3 | 14.3 [Go] | 1.23.0 | `ldmd2` |
| D | Build | Yes | 33.6 | 2.4 [Go] | v2.093.1-401-g164ef8f01 | `dmd` |
| D | Build | Yes | 213.2 | 15.3 [Go] | 1.23.0 | `ldmd2` |
| C | Check | No | 9.3 | 1.3 [D] | 8.4.0 | `gcc-8` |
| C | Check | No | 12.1 | 1.7 [D] | 9.3.0 | `gcc-9` |
| C | Check | No | 12.9 | 1.8 [D] | 10.2.0 | `gcc-10` |
| C | Check | No | 26.4 | 3.7 [D] | 8.0.1 | `clang-8` |
| C | Check | No | 29.4 | 4.2 [D] | 9.0.1 | `clang-9` |
| C | Check | No | 31.6 | 4.5 [D] | 10.0.0 | `clang-10` |
| C | Build | No | 388.5 | 27.9 [Go] | 8.4.0 | `gcc-8` |
| C | Build | No | 420.7 | 30.3 [Go] | 9.3.0 | `gcc-9` |
| C | Build | No | 430.6 | 31.0 [Go] | 10.2.0 | `gcc-10` |
| C | Build | No | 194.6 | 14.0 [Go] | 8.0.1 | `clang-8` |
| C | Build | No | 201.5 | 14.5 [Go] | 9.0.1 | `clang-9` |
| C | Build | No | 186.9 | 13.4 [Go] | 10.0.0 | `clang-10` |
| C++ | Check | No | 22.1 | 3.1 [D] | 8.4.0 | `g++-8` |
| C++ | Check | No | 34.9 | 4.9 [D] | 9.3.0 | `g++-9` |
| C++ | Check | No | 35.7 | 5.1 [D] | 10.2.0 | `g++-10` |
| C++ | Check | No | 34.8 | 4.9 [D] | 8.0.1 | `clang++-8` |
| C++ | Check | No | 36.8 | 5.2 [D] | 9.0.1 | `clang++-9` |
| C++ | Check | No | 39.1 | 5.5 [D] | 10.0.0 | `clang++-10` |
| C++ | Check | Yes | 58.9 | 8.3 [D] | 8.4.0 | `g++-8` |
| C++ | Check | Yes | 81.7 | 11.5 [D] | 9.3.0 | `g++-9` |
| C++ | Check | Yes | 82.8 | 11.7 [D] | 10.2.0 | `g++-10` |
| C++ | Check | Yes | 53.5 | 7.6 [D] | 8.0.1 | `clang++-8` |
| C++ | Check | Yes | 55.6 | 7.9 [D] | 9.0.1 | `clang++-9` |
| C++ | Check | Yes | 59.5 | 8.4 [D] | 10.0.0 | `clang++-10` |
| C++ | Build | No | 404.8 | 29.1 [Go] | 8.4.0 | `g++-8` |
| C++ | Build | No | 450.9 | 32.4 [Go] | 9.3.0 | `g++-9` |
| C++ | Build | No | 473.2 | 34.0 [Go] | 10.2.0 | `g++-10` |
| C++ | Build | No | 182.1 | 13.1 [Go] | 8.0.1 | `clang++-8` |
| C++ | Build | No | 191.6 | 13.8 [Go] | 9.0.1 | `clang++-9` |
| C++ | Build | No | 193.8 | 13.9 [Go] | 10.0.0 | `clang++-10` |
| C++ | Build | Yes | 8806.4 | 633.4 [Go] | 8.4.0 | `g++-8` |
| C++ | Build | Yes | 8671.1 | 623.7 [Go] | 9.3.0 | `g++-9` |
| C++ | Build | Yes | 8353.7 | 600.8 [Go] | 10.2.0 | `g++-10` |
| C++ | Build | Yes | 192.7 | 13.9 [Go] | 8.0.1 | `clang++-8` |
| C++ | Build | Yes | 207.0 | 14.9 [Go] | 9.0.1 | `clang++-9` |
| C++ | Build | Yes | 260.1 | 18.7 [Go] | 10.0.0 | `clang++-10` |
| Ada | Build | No | 5772.0 | 415.1 [Go] | 10.2.0 | `gnat-10` |
| Go | Check | No | 16.7 | 2.4 [D] | 1.15 | `gotype` |
| Go | Check | No | 24.9 | 3.5 [D] | 9.3.0 | `gccgo-9` |
| Go | Check | No | 26.1 | 3.7 [D] | 10.2.0 | `gccgo-10` |
| Go | Build | No | 13.9 | 1.0 [Go] | 1.15 | `go` |
| Go | Build | No | 35.7 | 2.6 [Go] | 9.3.0 | `gccgo-9` |
| Go | Build | No | 35.6 | 2.6 [Go] | 10.2.0 | `gccgo-10` |
| V | Build | No | 189.8 | 13.7 [Go] | 0.1.29 | `v` |
| Zig | Check | No | 88.3 | 12.5 [D] | 0.6.0+4e63cae36 | `zig` |
| Zig | Check | Yes | 122.8 | 17.4 [D] | 0.6.0+4e63cae36 | `zig` |
| Rust | Check | No | 466.6 | 66.0 [D] | 1.45.2 | `rustc` |
| Rust | Check | No | 264.9 | 37.5 [D] | 1.47.0-nightly | `rustc` |
| Rust | Check | Yes | 418.7 | 59.2 [D] | 1.45.2 | `rustc` |
| Rust | Check | Yes | 278.4 | 39.4 [D] | 1.47.0-nightly | `rustc` |
| Rust | Build | No | 779.8 | 56.1 [Go] | 1.45.2 | `rustc` |
| Rust | Build | No | 789.0 | 56.7 [Go] | 1.47.0-nightly | `rustc` |
| Rust | Build | Yes | 555.1 | 39.9 [Go] | 1.45.2 | `rustc` |
| Rust | Build | Yes | 488.1 | 35.1 [Go] | 1.47.0-nightly | `rustc` |
| C# | Build | No | 25.5 | 1.8 [Go] | 6.8.0.105 | `mcs` |
| Java | Build | No | 104.2 | 7.5 [Go] | 1.8.0_171 | `javac` |
| OCaml | Build | No | 72.2 | 5.2 [Go] | 4.08.1 | `ocamlc` |

This is with DMD built with LDC for an additional 15 percent drop in compilation time.

## TODO

- Put check and build time in separate columns on same line
- Measure link and run-time and add to columns
- Track memory usage of compilations using ideas at [Subprocess memory usage in python](https://stackoverflow.com/questions/13607391/subprocess-memory-usage-in-python/13607392).
- Parallelize calls to checkers and builders.
- Add language Fortran.

## References

- [Go compilation times compared to C++, D, Rust, Pascal (cross-posted)](https://www.reddit.com/r/golang/comments/55k7n4/go_compilation_times_compared_to_c_d_rust_pascal/)
