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
long add_long_n0_h0(long x) { return x + 0; }
long add_long_n0(long x) { return x + add_long_n0_h0(x) + 0; }

long add_long_n1_h0(long x) { return x + 1; }
long add_long_n1(long x) { return x + add_long_n1_h0(x) + 1; }

long add_long_n2_h0(long x) { return x + 2; }
long add_long_n2(long x) { return x + add_long_n2_h0(x) + 2; }


int main(__attribute__((unused)) int argc, __attribute__((unused)) char* argv[]) {
    long long_sum = 0;
    long_sum += add_long_n0(0);
    long_sum += add_long_n1(1);
    long_sum += add_long_n2(2);
    return long_sum;
}
```

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

The generic C++ and D (`dmd`) versions compiles about 1.5 to 2 times slower
whereas the generic Rust version interestingly is processed 2-3 times faster
than the non-generic version.

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

| Language | Templated | Oper | Exec Path | Exec Version | Time [s] | Slowdown vs [Best] |
| :---: | :---: | --- | :---: | :---: | :---: | :---: |
| D | No | Check | `~/.local/dlang/linux/bin64/dmd` | v2.093.0-320-g61fab1d67 | 0.601 | 1.7 [D] |
| D | No | Check | `~/.local/ldc2-1.23.0-beta1-linux-x86_64/bin/ldmd2` | 1.23.0-beta1 | 0.698 | 2.0 [D] |
| D | No | Check | `/usr/bin/gdc` | 10.0.1 | 0.684 | 1.9 [D] |
| D | Yes | Check | `~/.local/dlang/linux/bin64/dmd` | v2.093.0-320-g61fab1d67 | 1.512 | 4.3 [D] |
| D | Yes | Check | `~/.local/ldc2-1.23.0-beta1-linux-x86_64/bin/ldmd2` | 1.23.0-beta1 | 1.717 | 4.8 [D] |
| D | Yes | Check | `/usr/bin/gdc` | 10.0.1 | 0.355 | 1.0 [D] |
| D | No | Build | `~/.local/dlang/linux/bin64/dmd` | v2.093.0-320-g61fab1d67 | 1.470 | 4.1 [D] |
| D | No | Build | `~/.local/ldc2-1.23.0-beta1-linux-x86_64/bin/ldmd2` | 1.23.0-beta1 | 16.426 | 46.0 [D] |
| D | No | Build | `/usr/bin/gdc` | 10.0.1 | 38.032 | 106.6 [D] |
| D | Yes | Build | `~/.local/dlang/linux/bin64/dmd` | v2.093.0-320-g61fab1d67 | 2.509 | 7.0 [D] |
| D | Yes | Build | `~/.local/ldc2-1.23.0-beta1-linux-x86_64/bin/ldmd2` | 1.23.0-beta1 | 17.595 | 49.3 [D] |
| D | Yes | Build | `/usr/bin/gdc` | 10.0.1 | 0.357 | 1.0 [D] |
| C | No | Check | `/usr/bin/gcc-8` | 8.4.0 | 0.685 | 1.9 [D] |
| C | No | Check | `/usr/bin/gcc-9` | 9.3.0 | 1.018 | 2.9 [D] |
| C | No | Check | `/usr/bin/gcc-10` | 10 | 1.075 | 3.0 [D] |
| C | No | Check | `/usr/bin/clang-8` | 8.0.1 | 2.139 | 6.0 [D] |
| C | No | Check | `/usr/bin/clang-9` | 9.0.1 | 2.302 | 6.5 [D] |
| C | No | Check | `/usr/bin/clang-10` | 10.0.0 | 2.448 | 6.9 [D] |
| C | No | Build | `/usr/bin/gcc-8` | 8.4.0 | 31.561 | 88.4 [D] |
| C | No | Build | `/usr/bin/gcc-9` | 9.3.0 | 35.744 | 100.2 [D] |
| C | No | Build | `/usr/bin/gcc-10` | 10 | 36.874 | 103.3 [D] |
| C | No | Build | `/usr/bin/clang-8` | 8.0.1 | 14.577 | 40.8 [D] |
| C | No | Build | `/usr/bin/clang-9` | 9.0.1 | 15.063 | 42.2 [D] |
| C | No | Build | `/usr/bin/clang-10` | 10.0.0 | 15.530 | 43.5 [D] |
| C++ | No | Check | `/usr/bin/g++-8` | 8.4.0 | 1.748 | 4.9 [D] |
| C++ | No | Check | `/usr/bin/g++-9` | 9.3.0 | 2.780 | 7.8 [D] |
| C++ | No | Check | `/usr/bin/g++-10` | 10 | 3.040 | 8.6 [D] |
| C++ | No | Check | `/usr/bin/clang++-8` | 8.0.1 | 3.014 | 8.5 [D] |
| C++ | No | Check | `/usr/bin/clang++-9` | 9.0.1 | 3.126 | 8.8 [D] |
| C++ | No | Check | `/usr/bin/clang++-10` | 10.0.0 | 3.304 | 9.3 [D] |
| C++ | Yes | Check | `/usr/bin/g++-8` | 8.4.0 | 4.670 | 13.2 [D] |
| C++ | Yes | Check | `/usr/bin/g++-9` | 9.3.0 | 6.752 | 19.0 [D] |
| C++ | Yes | Check | `/usr/bin/g++-10` | 10 | 6.985 | 19.7 [D] |
| C++ | Yes | Check | `/usr/bin/clang++-8` | 8.0.1 | 4.628 | 13.0 [D] |
| C++ | Yes | Check | `/usr/bin/clang++-9` | 9.0.1 | 4.932 | 13.9 [D] |
| C++ | Yes | Check | `/usr/bin/clang++-10` | 10.0.0 | 5.060 | 14.3 [D] |
| C++ | No | Build | `/usr/bin/g++-8` | 8.4.0 | 33.158 | 92.9 [D] |
| C++ | No | Build | `/usr/bin/g++-9` | 9.3.0 | 38.363 | 107.5 [D] |
| C++ | No | Build | `/usr/bin/g++-10` | 10 | 39.532 | 110.8 [D] |
| C++ | No | Build | `/usr/bin/clang++-8` | 8.0.1 | 15.330 | 43.0 [D] |
| C++ | No | Build | `/usr/bin/clang++-9` | 9.0.1 | 16.179 | 45.3 [D] |
| C++ | No | Build | `/usr/bin/clang++-10` | 10.0.0 | 16.432 | 46.0 [D] |
| C++ | Yes | Build | `/usr/bin/g++-8` | 8.4.0 | 39.099 | 109.6 [D] |
| C++ | Yes | Build | `/usr/bin/g++-9` | 9.3.0 | 45.147 | 126.5 [D] |
| C++ | Yes | Build | `/usr/bin/g++-10` | 10 | 46.581 | 130.5 [D] |
| C++ | Yes | Build | `/usr/bin/clang++-8` | 8.0.1 | 16.653 | 46.7 [D] |
| C++ | Yes | Build | `/usr/bin/clang++-9` | 9.0.1 | 17.621 | 49.4 [D] |
| C++ | Yes | Build | `/usr/bin/clang++-10` | 10.0.0 | 22.637 | 63.4 [D] |
| Go | No | Check | `/usr/bin/gccgo` | 10.0.1 | 2.174 | 6.1 [D] |
| Go | No | Build | `/usr/bin/gccgo` | 10.0.1 | 55.009 | 154.2 [D] |
| V | No | Build | `~/ware/vlang/v` | 0.1.28 | 16.052 | 45.0 [D] |
| Zig | No | Check | `/snap/bin/zig` | 0.6.0+6123201f0 | 7.390 | 20.8 [D] |
| Zig | Yes | Check | `/snap/bin/zig` | 0.6.0+6123201f0 | 9.712 | 27.4 [D] |
| Rust | No | Check | `~/.cargo/bin/rustc` | 1.45.2 | 36.052 | 101.6 [D] |
| Rust | No | Check | `~/.cargo/bin/rustc` | 1.47.0-nightly | 21.744 | 61.3 [D] |
| Rust | Yes | Check | `~/.cargo/bin/rustc` | 1.45.2 | 34.106 | 96.1 [D] |
| Rust | Yes | Check | `~/.cargo/bin/rustc` | 1.47.0-nightly | 23.413 | 66.0 [D] |
| Rust | No | Build | `~/.cargo/bin/rustc` | 1.45.2 | 67.687 | 189.7 [D] |
| Rust | No | Build | `~/.cargo/bin/rustc` | 1.47.0-nightly | 68.045 | 190.7 [D] |
| Rust | Yes | Build | `~/.cargo/bin/rustc` | 1.45.2 | 43.141 | 120.9 [D] |
| Rust | Yes | Build | `~/.cargo/bin/rustc` | 1.47.0-nightly | 41.917 | 117.5 [D] |
| Java | No | Build | `/usr/bin/javac` | 1.8.0_171 | 7.722 | 21.6 [D] |
| OCaml | No | Build | `/usr/bin/ocamlc` | 4.08.1 | 6.200 | 17.4 [D] |

This is with DMD built with LDC for an additional 15 percent drop in compilation time.

## TODO

- Track memory usage of compilations using ideas at [Subprocess memory usage in python](https://stackoverflow.com/questions/13607391/subprocess-memory-usage-in-python/13607392).
- Parallelize calls to checkers and builders.
- Add language Fortran.
- Add language Ada and do syntax checking using `-gnats`. See: https://gcc.gnu.org/onlinedocs/gcc-4.7.4/gnat_ugn_unw/Using-gcc-for-Syntax-Checking.html
