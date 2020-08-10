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
is to make the comparison between compilers more fair.

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
| D | Check | No | 0.620 | 1.0 [D] | v2.093.0-344-ga1cb3f44c | `dmd` |
| D | Check | No | 0.700 | 1.1 [D] | 1.23.0-beta1 | `ldmd2` |
| D | Check | Yes | 1.470 | 2.4 [D] | v2.093.0-344-ga1cb3f44c | `dmd` |
| D | Check | Yes | 1.681 | 2.7 [D] | 1.23.0-beta1 | `ldmd2` |
| D | Build | No | 1.444 | 1.0 [D] | v2.093.0-344-ga1cb3f44c | `dmd` |
| D | Build | No | 18.251 | 12.6 [D] | 1.23.0-beta1 | `ldmd2` |
| D | Build | Yes | 2.593 | 1.8 [D] | v2.093.0-344-ga1cb3f44c | `dmd` |
| D | Build | Yes | 18.227 | 12.6 [D] | 1.23.0-beta1 | `ldmd2` |
| C | Check | No | 0.696 | 1.1 [D] | 8.4.0 | `gcc-8` |
| C | Check | No | 1.036 | 1.7 [D] | 9.3.0 | `gcc-9` |
| C | Check | No | 1.087 | 1.8 [D] | 10 | `gcc-10` |
| C | Check | No | 2.170 | 3.5 [D] | 8.0.1 | `clang-8` |
| C | Check | No | 2.550 | 4.1 [D] | 9.0.1 | `clang-9` |
| C | Check | No | 2.508 | 4.0 [D] | 10.0.0 | `clang-10` |
| C | Build | No | 32.086 | 22.2 [D] | 8.4.0 | `gcc-8` |
| C | Build | No | 35.975 | 24.9 [D] | 9.3.0 | `gcc-9` |
| C | Build | No | 38.517 | 26.7 [D] | 10 | `gcc-10` |
| C | Build | No | 14.913 | 10.3 [D] | 8.0.1 | `clang-8` |
| C | Build | No | 15.661 | 10.8 [D] | 9.0.1 | `clang-9` |
| C | Build | No | 16.414 | 11.4 [D] | 10.0.0 | `clang-10` |
| C++ | Check | No | 1.762 | 2.8 [D] | 8.4.0 | `g++-8` |
| C++ | Check | No | 3.131 | 5.0 [D] | 9.3.0 | `g++-9` |
| C++ | Check | No | 3.145 | 5.1 [D] | 10 | `g++-10` |
| C++ | Check | No | 3.120 | 5.0 [D] | 8.0.1 | `clang++-8` |
| C++ | Check | No | 3.255 | 5.2 [D] | 9.0.1 | `clang++-9` |
| C++ | Check | No | 3.380 | 5.4 [D] | 10.0.0 | `clang++-10` |
| C++ | Check | Yes | 5.323 | 8.6 [D] | 8.4.0 | `g++-8` |
| C++ | Check | Yes | 7.286 | 11.7 [D] | 9.3.0 | `g++-9` |
| C++ | Check | Yes | 7.358 | 11.9 [D] | 10 | `g++-10` |
| C++ | Check | Yes | 4.799 | 7.7 [D] | 8.0.1 | `clang++-8` |
| C++ | Check | Yes | 5.097 | 8.2 [D] | 9.0.1 | `clang++-9` |
| C++ | Check | Yes | 5.354 | 8.6 [D] | 10.0.0 | `clang++-10` |
| C++ | Build | No | 34.819 | 24.1 [D] | 8.4.0 | `g++-8` |
| C++ | Build | No | 39.132 | 27.1 [D] | 9.3.0 | `g++-9` |
| C++ | Build | No | 40.489 | 28.0 [D] | 10 | `g++-10` |
| C++ | Build | No | 15.827 | 11.0 [D] | 8.0.1 | `clang++-8` |
| C++ | Build | No | 16.398 | 11.4 [D] | 9.0.1 | `clang++-9` |
| C++ | Build | No | 16.878 | 11.7 [D] | 10.0.0 | `clang++-10` |
| C++ | Build | Yes | 40.539 | 28.1 [D] | 8.4.0 | `g++-8` |
| C++ | Build | Yes | 47.433 | 32.8 [D] | 9.3.0 | `g++-9` |
| C++ | Build | Yes | 48.699 | 33.7 [D] | 10 | `g++-10` |
| C++ | Build | Yes | 18.964 | 13.1 [D] | 8.0.1 | `clang++-8` |
| C++ | Build | Yes | 19.046 | 13.2 [D] | 9.0.1 | `clang++-9` |
| C++ | Build | Yes | 24.981 | 17.3 [D] | 10.0.0 | `clang++-10` |
| Go | Check | No | 2.308 | 3.7 [D] | 10.0.1 | `gccgo` |
| Go | Build | No | 58.561 | 40.5 [D] | 10.0.1 | `gccgo` |
| V | Build | No | 16.350 | 11.3 [D] | 0.1.28 | `v` |
| Zig | Check | No | 7.676 | 12.4 [D] | 0.6.0+cf4936bcb | `zig` |
| Zig | Check | Yes | 10.146 | 16.4 [D] | 0.6.0+cf4936bcb | `zig` |
| Rust | Check | No | 37.409 | 60.3 [D] | 1.45.2 | `rustc` |
| Rust | Check | No | 23.378 | 37.7 [D] | 1.47.0-nightly | `rustc` |
| Rust | Check | Yes | 35.557 | 57.3 [D] | 1.45.2 | `rustc` |
| Rust | Check | Yes | 24.342 | 39.2 [D] | 1.47.0-nightly | `rustc` |
| Rust | Build | No | 70.577 | 48.9 [D] | 1.45.2 | `rustc` |
| Rust | Build | No | 70.312 | 48.7 [D] | 1.47.0-nightly | `rustc` |
| Rust | Build | Yes | 45.144 | 31.3 [D] | 1.45.2 | `rustc` |
| Rust | Build | Yes | 46.504 | 32.2 [D] | 1.47.0-nightly | `rustc` |
| Java | Build | No | 8.782 | 6.1 [D] | 1.8.0_171 | `javac` |
| OCaml | Build | No | 8.441 | 5.8 [D] | 4.08.1 | `ocamlc` |

This is with DMD built with LDC for an additional 15 percent drop in compilation time.

## TODO

- Track memory usage of compilations using ideas at [Subprocess memory usage in python](https://stackoverflow.com/questions/13607391/subprocess-memory-usage-in-python/13607392).
- Parallelize calls to checkers and builders.
- Add language Fortran.
- Add language Ada and do syntax checking using `-gnats`. See: https://gcc.gnu.org/onlinedocs/gcc-4.7.4/gnat_ugn_unw/Using-gcc-for-Syntax-Checking.html
