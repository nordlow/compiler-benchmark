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

| Lang-uage | Oper-ation | Temp-lated | Exec Path | Exec Version | Time [s] | Slowdown vs [Best] |
| :---: | :---: | --- | :---: | :---: | :---: | :---: |
| D | Check | No | `~/.local/dlang/linux/bin64/dmd` | v2.093.0-344-ga1cb3f44c | 0.608 | 1.0 [D] |
| D | Check | No | `~/.local/ldc2-1.23.0-beta1-linux-x86_64/bin/ldmd2` | 1.23.0-beta1 | 0.693 | 1.1 [D] |
| D | Check | Yes | `~/.local/dlang/linux/bin64/dmd` | v2.093.0-344-ga1cb3f44c | 1.468 | 2.4 [D] |
| D | Check | Yes | `~/.local/ldc2-1.23.0-beta1-linux-x86_64/bin/ldmd2` | 1.23.0-beta1 | 1.675 | 2.8 [D] |
| D | Build | No | `~/.local/dlang/linux/bin64/dmd` | v2.093.0-344-ga1cb3f44c | 1.450 | 1.0 [D] |
| D | Build | No | `~/.local/ldc2-1.23.0-beta1-linux-x86_64/bin/ldmd2` | 1.23.0-beta1 | 16.460 | 11.3 [D] |
| D | Build | Yes | `~/.local/dlang/linux/bin64/dmd` | v2.093.0-344-ga1cb3f44c | 2.522 | 1.7 [D] |
| D | Build | Yes | `~/.local/ldc2-1.23.0-beta1-linux-x86_64/bin/ldmd2` | 1.23.0-beta1 | 17.794 | 12.3 [D] |
| C | Check | No | `/usr/bin/gcc-8` | 8.4.0 | 0.723 | 1.2 [D] |
| C | Check | No | `/usr/bin/gcc-9` | 9.3.0 | 1.026 | 1.7 [D] |
| C | Check | No | `/usr/bin/gcc-10` | 10 | 1.101 | 1.8 [D] |
| C | Check | No | `/usr/bin/clang-8` | 8.0.1 | 2.223 | 3.7 [D] |
| C | Check | No | `/usr/bin/clang-9` | 9.0.1 | 2.371 | 3.9 [D] |
| C | Check | No | `/usr/bin/clang-10` | 10.0.0 | 2.541 | 4.2 [D] |
| C | Build | No | `/usr/bin/gcc-8` | 8.4.0 | 32.314 | 22.3 [D] |
| C | Build | No | `/usr/bin/gcc-9` | 9.3.0 | 37.659 | 26.0 [D] |
| C | Build | No | `/usr/bin/gcc-10` | 10 | 37.562 | 25.9 [D] |
| C | Build | No | `/usr/bin/clang-8` | 8.0.1 | 14.734 | 10.2 [D] |
| C | Build | No | `/usr/bin/clang-9` | 9.0.1 | 15.445 | 10.6 [D] |
| C | Build | No | `/usr/bin/clang-10` | 10.0.0 | 15.638 | 10.8 [D] |
| C++ | Check | No | `/usr/bin/g++-8` | 8.4.0 | 1.751 | 2.9 [D] |
| C++ | Check | No | `/usr/bin/g++-9` | 9.3.0 | 2.793 | 4.6 [D] |
| C++ | Check | No | `/usr/bin/g++-10` | 10 | 3.033 | 5.0 [D] |
| C++ | Check | No | `/usr/bin/clang++-8` | 8.0.1 | 3.048 | 5.0 [D] |
| C++ | Check | No | `/usr/bin/clang++-9` | 9.0.1 | 3.200 | 5.3 [D] |
| C++ | Check | No | `/usr/bin/clang++-10` | 10.0.0 | 3.352 | 5.5 [D] |
| C++ | Check | Yes | `/usr/bin/g++-8` | 8.4.0 | 4.785 | 7.9 [D] |
| C++ | Check | Yes | `/usr/bin/g++-9` | 9.3.0 | 7.069 | 11.6 [D] |
| C++ | Check | Yes | `/usr/bin/g++-10` | 10 | 7.122 | 11.7 [D] |
| C++ | Check | Yes | `/usr/bin/clang++-8` | 8.0.1 | 4.698 | 7.7 [D] |
| C++ | Check | Yes | `/usr/bin/clang++-9` | 9.0.1 | 4.883 | 8.0 [D] |
| C++ | Check | Yes | `/usr/bin/clang++-10` | 10.0.0 | 5.264 | 8.7 [D] |
| C++ | Build | No | `/usr/bin/g++-8` | 8.4.0 | 34.044 | 23.5 [D] |
| C++ | Build | No | `/usr/bin/g++-9` | 9.3.0 | 38.895 | 26.8 [D] |
| C++ | Build | No | `/usr/bin/g++-10` | 10 | 40.564 | 28.0 [D] |
| C++ | Build | No | `/usr/bin/clang++-8` | 8.0.1 | 15.817 | 10.9 [D] |
| C++ | Build | No | `/usr/bin/clang++-9` | 9.0.1 | 16.553 | 11.4 [D] |
| C++ | Build | No | `/usr/bin/clang++-10` | 10.0.0 | 16.688 | 11.5 [D] |
| C++ | Build | Yes | `/usr/bin/g++-8` | 8.4.0 | 41.221 | 28.4 [D] |
| C++ | Build | Yes | `/usr/bin/g++-9` | 9.3.0 | 46.374 | 32.0 [D] |
| C++ | Build | Yes | `/usr/bin/g++-10` | 10 | 48.071 | 33.1 [D] |
| C++ | Build | Yes | `/usr/bin/clang++-8` | 8.0.1 | 17.607 | 12.1 [D] |
| C++ | Build | Yes | `/usr/bin/clang++-9` | 9.0.1 | 18.019 | 12.4 [D] |
| C++ | Build | Yes | `/usr/bin/clang++-10` | 10.0.0 | 23.332 | 16.1 [D] |
| Go | Check | No | `/usr/bin/gccgo` | 10.0.1 | 2.196 | 3.6 [D] |
| Go | Build | No | `/usr/bin/gccgo` | 10.0.1 | 56.585 | 39.0 [D] |
| Zig | Check | No | `/snap/bin/zig` | 0.6.0+4ab2f947f | 7.619 | 12.5 [D] |
| Zig | Check | Yes | `/snap/bin/zig` | 0.6.0+4ab2f947f | 9.857 | 16.2 [D] |
| Rust | Check | No | `~/.cargo/bin/rustc` | 1.45.2 | 37.031 | 60.9 [D] |
| Rust | Check | No | `~/.cargo/bin/rustc` | 1.47.0-nightly | 22.318 | 36.7 [D] |
| Rust | Check | Yes | `~/.cargo/bin/rustc` | 1.45.2 | 34.483 | 56.7 [D] |
| Rust | Check | Yes | `~/.cargo/bin/rustc` | 1.47.0-nightly | 23.938 | 39.3 [D] |
| Rust | Build | No | `~/.cargo/bin/rustc` | 1.45.2 | 68.980 | 47.6 [D] |
| Rust | Build | No | `~/.cargo/bin/rustc` | 1.47.0-nightly | 69.173 | 47.7 [D] |
| Rust | Build | Yes | `~/.cargo/bin/rustc` | 1.45.2 | 43.434 | 29.9 [D] |
| Rust | Build | Yes | `~/.cargo/bin/rustc` | 1.47.0-nightly | 42.521 | 29.3 [D] |
| Java | Build | No | `/usr/bin/javac` | 1.8.0_171 | 8.060 | 5.6 [D] |
| OCaml | Build | No | `/usr/bin/ocamlc` | 4.08.1 | 6.207 | 4.3 [D] |

This is with DMD built with LDC for an additional 15 percent drop in compilation time.

## TODO

- Track memory usage of compilations using ideas at [Subprocess memory usage in python](https://stackoverflow.com/questions/13607391/subprocess-memory-usage-in-python/13607392).
- Parallelize calls to checkers and builders.
- Add language Fortran.
- Add language Ada and do syntax checking using `-gnats`. See: https://gcc.gnu.org/onlinedocs/gcc-4.7.4/gnat_ugn_unw/Using-gcc-for-Syntax-Checking.html
