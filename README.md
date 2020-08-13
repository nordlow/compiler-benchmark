# compiler-benchmark

Benchmarks compilation speeds of different combinations of languages and
compilers. Supported languages are

- C (using `gcc`),
- C++ (using `g++`),
- D (using `dmd` `ldmd2`, and `gdc`),
- Go (using `gccgo`),
- Rust (using `rustc`),
- V (using `v`),
- Zig (using `zig`),
- OCaml (using `ocamlopt`),
- Julia (using `julia`) and
- Java (using `javac`).

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
benchmark is printed to standard output.

GCC and Clang doesn't perform all semantic checks for C++ (because it's too
costly). This is in contrast to D's and Rust's compilers that perform all of
them.

## Sample generated code

To understand how the code generation works we can, for instance, do

    ./benchmark --function-count=3 --function-depth=2 --run-count=5

This will, for the C language case, generate a file `generated/c/linear.c` containing

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
file `linear_t.$LANG` will be generated alongside `linear.$LANG` equivalent to
the contents of `linear.$LANG` apart from that all functions (except `main`) are
templated. This templated source will be benchmarked aswell. The column
**Templated** in the table below indicates whether or not the compilation is
using templated functions.

## Conclusions (from sample run shown below)

D's compiler `dmd` is still far ahead of all its competition especially when it
comes to default build (standard compilation) performance.

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

| Lang-uage | Oper-ation | Temp-lated | Time [s] | Slowdown vs [Best] | Version | Exec |
| :---: | :---: | --- | :---: | :---: | :---: | :---: |
| D | Check | No | 0.626 | 1.0 [D] | v2.065.0-16538-g8b93911d7 | `dmd` |
| D | Check | No | 0.703 | 1.1 [D] | 1.23.0-beta1 | `ldmd2` |
| D | Check | Yes | 1.566 | 2.5 [D] | v2.065.0-16538-g8b93911d7 | `dmd` |
| D | Check | Yes | 1.724 | 2.8 [D] | 1.23.0-beta1 | `ldmd2` |
| D | Build | No | 1.464 | 1.0 [D] | v2.065.0-16538-g8b93911d7 | `dmd` |
| D | Build | No | 17.063 | 11.7 [D] | 1.23.0-beta1 | `ldmd2` |
| D | Build | Yes | 2.570 | 1.8 [D] | v2.065.0-16538-g8b93911d7 | `dmd` |
| D | Build | Yes | 18.166 | 12.4 [D] | 1.23.0-beta1 | `ldmd2` |
| C | Check | No | 0.771 | 1.2 [D] | 8.4.0 | `gcc-8` |
| C | Check | No | 1.187 | 1.9 [D] | 9.3.0 | `gcc-9` |
| C | Check | No | 1.163 | 1.9 [D] | 10 | `gcc-10` |
| C | Check | No | 2.243 | 3.6 [D] | 8.0.1 | `clang-8` |
| C | Check | No | 2.396 | 3.8 [D] | 9.0.1 | `clang-9` |
| C | Check | No | 2.580 | 4.1 [D] | 10.0.0 | `clang-10` |
| C | Build | No | 32.853 | 22.4 [D] | 8.4.0 | `gcc-8` |
| C | Build | No | 37.006 | 25.3 [D] | 9.3.0 | `gcc-9` |
| C | Build | No | 38.175 | 26.1 [D] | 10 | `gcc-10` |
| C | Build | No | 15.155 | 10.4 [D] | 8.0.1 | `clang-8` |
| C | Build | No | 15.703 | 10.7 [D] | 9.0.1 | `clang-9` |
| C | Build | No | 15.923 | 10.9 [D] | 10.0.0 | `clang-10` |
| C++ | Check | No | 1.871 | 3.0 [D] | 8.4.0 | `g++-8` |
| C++ | Check | No | 3.051 | 4.9 [D] | 9.3.0 | `g++-9` |
| C++ | Check | No | 3.169 | 5.1 [D] | 10 | `g++-10` |
| C++ | Check | No | 3.133 | 5.0 [D] | 8.0.1 | `clang++-8` |
| C++ | Check | No | 3.243 | 5.2 [D] | 9.0.1 | `clang++-9` |
| C++ | Check | No | 3.402 | 5.4 [D] | 10.0.0 | `clang++-10` |
| C++ | Check | Yes | 5.289 | 8.5 [D] | 8.4.0 | `g++-8` |
| C++ | Check | Yes | 7.216 | 11.5 [D] | 9.3.0 | `g++-9` |
| C++ | Check | Yes | 7.507 | 12.0 [D] | 10 | `g++-10` |
| C++ | Check | Yes | 4.867 | 7.8 [D] | 8.0.1 | `clang++-8` |
| C++ | Check | Yes | 5.017 | 8.0 [D] | 9.0.1 | `clang++-9` |
| C++ | Check | Yes | 5.259 | 8.4 [D] | 10.0.0 | `clang++-10` |
| C++ | Build | No | 34.703 | 23.7 [D] | 8.4.0 | `g++-8` |
| C++ | Build | No | 39.565 | 27.0 [D] | 9.3.0 | `g++-9` |
| C++ | Build | No | 40.917 | 28.0 [D] | 10 | `g++-10` |
| C++ | Build | No | 16.134 | 11.0 [D] | 8.0.1 | `clang++-8` |
| C++ | Build | No | 16.887 | 11.5 [D] | 9.0.1 | `clang++-9` |
| C++ | Build | No | 16.873 | 11.5 [D] | 10.0.0 | `clang++-10` |
| C++ | Build | Yes | 727.064 | 496.7 [D] | 8.4.0 | `g++-8` |
| C++ | Build | Yes | 731.143 | 499.5 [D] | 9.3.0 | `g++-9` |
| C++ | Build | Yes | 732.324 | 500.3 [D] | 10 | `g++-10` |
| C++ | Build | Yes | 17.030 | 11.6 [D] | 8.0.1 | `clang++-8` |
| C++ | Build | Yes | 17.865 | 12.2 [D] | 9.0.1 | `clang++-9` |
| C++ | Build | Yes | 23.439 | 16.0 [D] | 10.0.0 | `clang++-10` |
| Go | Check | No | 2.260 | 3.6 [D] | 10.0.1 | `gccgo` |
| Go | Build | No | 57.132 | 39.0 [D] | 10.0.1 | `gccgo` |
| V | Build | No | 16.331 | 11.2 [D] | 0.1.29 | `v` |
| Zig | Check | No | 7.729 | 12.4 [D] | 0.6.0+7612931c8 | `zig` |
| Zig | Check | Yes | 10.030 | 16.0 [D] | 0.6.0+7612931c8 | `zig` |
| Rust | Check | No | 38.048 | 60.8 [D] | 1.45.2 | `rustc` |
| Rust | Check | No | 22.534 | 36.0 [D] | 1.47.0-nightly | `rustc` |
| Rust | Check | Yes | 34.962 | 55.9 [D] | 1.45.2 | `rustc` |
| Rust | Check | Yes | 24.045 | 38.4 [D] | 1.47.0-nightly | `rustc` |
| Rust | Build | No | 72.882 | 49.8 [D] | 1.45.2 | `rustc` |
| Rust | Build | No | 73.344 | 50.1 [D] | 1.47.0-nightly | `rustc` |
| Rust | Build | Yes | 46.048 | 31.5 [D] | 1.45.2 | `rustc` |
| Rust | Build | Yes | 44.809 | 30.6 [D] | 1.47.0-nightly | `rustc` |
| Java | Build | No | 7.858 | 5.4 [D] | 1.8.0_171 | `javac` |
| OCaml | Build | No | 6.482 | 4.4 [D] | 4.08.1 | `ocamlc` |

This is with DMD built with LDC for an additional 15 percent drop in compilation time.

## TODO

- Add language C# via `mono`
- Put check and build time in separate columns on same line
- Measure link and run-time
- Track memory usage of compilations using ideas at [Subprocess memory usage in python](https://stackoverflow.com/questions/13607391/subprocess-memory-usage-in-python/13607392).
- Parallelize calls to checkers and builders.
- Add language Fortran.
- Add language Ada and do syntax checking using `-gnats`. See: https://gcc.gnu.org/onlinedocs/gcc-4.7.4/gnat_ugn_unw/Using-gcc-for-Syntax-Checking.html
