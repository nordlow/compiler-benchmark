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
benchmark is printed to standard output.

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

| Lang-uage | Oper-ation | Temp-lated | Time [s/fn] | Slowdown vs [Best] | Version | Exec |
| :---: | :---: | --- | :---: | :---: | :---: | :---: |
| D | Check | No | 0.586 | 1.0 [D] | v2.093.1-beta.1-376-gbdaf4703c | `dmd` |
| D | Check | No | 0.683 | 1.2 [D] | 1.23.0-beta1 | `ldmd2` |
| D | Check | Yes | 1.526 | 2.6 [D] | v2.093.1-beta.1-376-gbdaf4703c | `dmd` |
| D | Check | Yes | 1.682 | 2.9 [D] | 1.23.0-beta1 | `ldmd2` |
| D | Build | No | 1.447 | 1.0 [D] | v2.093.1-beta.1-376-gbdaf4703c | `dmd` |
| D | Build | No | 16.960 | 11.7 [D] | 1.23.0-beta1 | `ldmd2` |
| D | Build | Yes | 2.585 | 1.8 [D] | v2.093.1-beta.1-376-gbdaf4703c | `dmd` |
| D | Build | Yes | 18.352 | 12.7 [D] | 1.23.0-beta1 | `ldmd2` |
| C | Check | No | 0.790 | 1.3 [D] | 8.4.0 | `gcc-8` |
| C | Check | No | 1.109 | 1.9 [D] | 9.3.0 | `gcc-9` |
| C | Check | No | 1.157 | 2.0 [D] | 10 | `gcc-10` |
| C | Check | No | 2.211 | 3.8 [D] | 8.0.1 | `clang-8` |
| C | Check | No | 2.422 | 4.1 [D] | 9.0.1 | `clang-9` |
| C | Check | No | 2.598 | 4.4 [D] | 10.0.0 | `clang-10` |
| C | Build | No | 32.750 | 22.6 [D] | 8.4.0 | `gcc-8` |
| C | Build | No | 36.760 | 25.4 [D] | 9.3.0 | `gcc-9` |
| C | Build | No | 38.480 | 26.6 [D] | 10 | `gcc-10` |
| C | Build | No | 15.074 | 10.4 [D] | 8.0.1 | `clang-8` |
| C | Build | No | 15.718 | 10.9 [D] | 9.0.1 | `clang-9` |
| C | Build | No | 15.913 | 11.0 [D] | 10.0.0 | `clang-10` |
| C++ | Check | No | 1.821 | 3.1 [D] | 8.4.0 | `g++-8` |
| C++ | Check | No | 3.009 | 5.1 [D] | 9.3.0 | `g++-9` |
| C++ | Check | No | 3.186 | 5.4 [D] | 10 | `g++-10` |
| C++ | Check | No | 3.098 | 5.3 [D] | 8.0.1 | `clang++-8` |
| C++ | Check | No | 3.277 | 5.6 [D] | 9.0.1 | `clang++-9` |
| C++ | Check | No | 3.374 | 5.8 [D] | 10.0.0 | `clang++-10` |
| C++ | Check | Yes | 5.083 | 8.7 [D] | 8.4.0 | `g++-8` |
| C++ | Check | Yes | 6.993 | 11.9 [D] | 9.3.0 | `g++-9` |
| C++ | Check | Yes | 7.289 | 12.4 [D] | 10 | `g++-10` |
| C++ | Check | Yes | 4.784 | 8.2 [D] | 8.0.1 | `clang++-8` |
| C++ | Check | Yes | 4.887 | 8.3 [D] | 9.0.1 | `clang++-9` |
| C++ | Check | Yes | 5.264 | 9.0 [D] | 10.0.0 | `clang++-10` |
| C++ | Build | No | 34.533 | 23.9 [D] | 8.4.0 | `g++-8` |
| C++ | Build | No | 39.583 | 27.4 [D] | 9.3.0 | `g++-9` |
| C++ | Build | No | 40.962 | 28.3 [D] | 10 | `g++-10` |
| C++ | Build | No | 16.074 | 11.1 [D] | 8.0.1 | `clang++-8` |
| C++ | Build | No | 16.762 | 11.6 [D] | 9.0.1 | `clang++-9` |
| C++ | Build | No | 16.940 | 11.7 [D] | 10.0.0 | `clang++-10` |
| C++ | Build | Yes | 714.725 | 494.1 [D] | 8.4.0 | `g++-8` |
| C++ | Build | Yes | 722.095 | 499.2 [D] | 9.3.0 | `g++-9` |
| C++ | Build | Yes | 725.300 | 501.4 [D] | 10 | `g++-10` |
| C++ | Build | Yes | 17.097 | 11.8 [D] | 8.0.1 | `clang++-8` |
| C++ | Build | Yes | 17.991 | 12.4 [D] | 9.0.1 | `clang++-9` |
| C++ | Build | Yes | 23.222 | 16.1 [D] | 10.0.0 | `clang++-10` |
| Go | Check | No | 2.241 | 3.8 [D] | 10.0.1 | `gccgo` |
| Go | Build | No | 56.780 | 39.3 [D] | 10.0.1 | `gccgo` |
| V | Build | No | 16.307 | 11.3 [D] | 0.1.29 | `v` |
| Zig | Check | No | 7.636 | 13.0 [D] | 0.6.0+6e0fb0601 | `zig` |
| Zig | Check | Yes | 9.997 | 17.1 [D] | 0.6.0+6e0fb0601 | `zig` |
| Rust | Check | No | 37.826 | 64.5 [D] | 1.45.2 | `rustc` |
| Rust | Check | No | 23.063 | 39.3 [D] | 1.47.0-nightly | `rustc` |
| Rust | Check | Yes | 35.276 | 60.2 [D] | 1.45.2 | `rustc` |
| Rust | Check | Yes | 24.744 | 42.2 [D] | 1.47.0-nightly | `rustc` |
| Rust | Build | No | 73.037 | 50.5 [D] | 1.45.2 | `rustc` |
| Rust | Build | No | 73.920 | 51.1 [D] | 1.47.0-nightly | `rustc` |
| Rust | Build | Yes | 45.968 | 31.8 [D] | 1.45.2 | `rustc` |
| Rust | Build | Yes | 45.797 | 31.7 [D] | 1.47.0-nightly | `rustc` |
| C# | Build | No | 2.254 | 1.6 [D] | 6.8.0.105 | `mcs` |
| Java | Build | No | 8.295 | 5.7 [D] | 1.8.0_171 | `javac` |
| OCaml | Build | No | 6.464 | 4.5 [D] | 4.08.1 | `ocamlc` |

This is with DMD built with LDC for an additional 15 percent drop in compilation time.

## TODO

- Put check and build time in separate columns on same line
- Measure link and run-time and add to columns
- Track memory usage of compilations using ideas at [Subprocess memory usage in python](https://stackoverflow.com/questions/13607391/subprocess-memory-usage-in-python/13607392).
- Parallelize calls to checkers and builders.
- Add language Fortran.
- Add language Ada and do syntax checking using `-gnats`. See: https://gcc.gnu.org/onlinedocs/gcc-4.7.4/gnat_ugn_unw/Using-gcc-for-Syntax-Checking.html

## References

- [Go compilation times compared to C++, D, Rust, Pascal (cross-posted)](https://www.reddit.com/r/golang/comments/55k7n4/go_compilation_times_compared_to_c_d_rust_pascal/)
