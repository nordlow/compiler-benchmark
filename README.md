# compiler-benchmark

Benchmarks compilation speeds of different combinations of languages and
compilers. Currently supports

- C (using `gcc`),
- C++ (using `g++`),
- D (using `dmd` and `ldmd2`),
- Go (using `gccgo`),
- Rust (using `rustc`),
- V (using `v`),
- Zig (using `zig`),
- Julia (using `julia`) and
- Java (using `javac`).

## How it works

Typically run the benchmark as

    ./benchmark --function-count=$FUNCTION_COUNT --function-depth=$FUNCTION_DEPTH --run-count=5

for suitable values of `$FUNCTION_COUNT` and `FUNCTION_DEPTH` or simply

    ./benchmark

for defaulted values of all the parameters.

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

For each languages that supports generics an additional templated source file
`linear_t.$LANG` will be generated alongside `linear.$LANG` equivalent to the
contents of `linear.$LANG` apart from that all functions (except `main`) are
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

## Sample run output

The output on my Intel® Core™ i7-4710HQ CPU @ 2.50GHz × 8 with 16 GB of memory
running Ubuntu 20.04 for the sample call

    ./benchmark --function-count=200 --function-depth=450 --run-count=10

results in the following table (copied from the output at the end).

| Language | Templated | Oper | Exec Path | Exec Version | Time [s] | Time vs D |
| :---: | :---: | --- | :---: | :---: | :---: | :---: |
| D | No | Check | `~/.local/dlang/linux/bin64/dmd` | v2.093.0-199-g25a0741cb | 0.645 | N/A |
| D | No | Check | `~/.local/ldc2-1.22.0-linux-x86_64/bin/ldmd2` | 1.22.0 | 0.714 | N/A |
| D | Yes | Check | `~/.local/dlang/linux/bin64/dmd` | v2.093.0-199-g25a0741cb | 1.698 | N/A |
| D | Yes | Check | `~/.local/ldc2-1.22.0-linux-x86_64/bin/ldmd2` | 1.22.0 | 1.894 | N/A |
| D | No | Build | `~/.local/dlang/linux/bin64/dmd` | v2.093.0-199-g25a0741cb | 1.591 | N/A |
| D | No | Build | `~/.local/ldc2-1.22.0-linux-x86_64/bin/ldmd2` | 1.22.0 | 16.680 | N/A |
| D | Yes | Build | `~/.local/dlang/linux/bin64/dmd` | v2.093.0-199-g25a0741cb | 2.583 | N/A |
| D | Yes | Build | `~/.local/ldc2-1.22.0-linux-x86_64/bin/ldmd2` | 1.22.0 | 17.637 | N/A |
| C | No | Check | `/usr/bin/gcc-8` | 8.4.0 | 0.716 | 1.1 |
| C | No | Check | `/usr/bin/gcc-9` | 9.3.0 | 1.020 | 1.6 |
| C | No | Check | `/usr/bin/gcc-10` | 10 | 1.095 | 1.7 |
| C | No | Check | `/usr/bin/clang-8` | 8.0.1 | 2.174 | 3.4 |
| C | No | Check | `/usr/bin/clang-9` | 9.0.1 | 2.353 | 3.7 |
| C | No | Check | `/usr/bin/clang-10` | 10.0.0 | 2.718 | 4.2 |
| C | No | Build | `/usr/bin/gcc-8` | 8.4.0 | 32.558 | 20.5 |
| C | No | Build | `/usr/bin/gcc-9` | 9.3.0 | 38.209 | 24.0 |
| C | No | Build | `/usr/bin/gcc-10` | 10 | 40.527 | 25.5 |
| C | No | Build | `/usr/bin/clang-8` | 8.0.1 | 16.224 | 10.2 |
| C | No | Build | `/usr/bin/clang-9` | 9.0.1 | 16.821 | 10.6 |
| C | No | Build | `/usr/bin/clang-10` | 10.0.0 | 17.069 | 10.7 |
| C++ | No | Check | `/usr/bin/g++-8` | 8.4.0 | 1.882 | 2.9 |
| C++ | No | Check | `/usr/bin/g++-9` | 9.3.0 | 2.993 | 4.6 |
| C++ | No | Check | `/usr/bin/g++-10` | 10 | 3.217 | 5.0 |
| C++ | No | Check | `/usr/bin/clang++-8` | 8.0.1 | 3.297 | 5.1 |
| C++ | No | Check | `/usr/bin/clang++-9` | 9.0.1 | 3.524 | 5.5 |
| C++ | No | Check | `/usr/bin/clang++-10` | 10.0.0 | 3.689 | 5.7 |
| C++ | Yes | Check | `/usr/bin/g++-8` | 8.4.0 | 5.880 | 3.5 |
| C++ | Yes | Check | `/usr/bin/g++-9` | 9.3.0 | 7.501 | 4.4 |
| C++ | Yes | Check | `/usr/bin/g++-10` | 10 | 7.787 | 4.6 |
| C++ | Yes | Check | `/usr/bin/clang++-8` | 8.0.1 | 4.997 | 2.9 |
| C++ | Yes | Check | `/usr/bin/clang++-9` | 9.0.1 | 5.226 | 3.1 |
| C++ | Yes | Check | `/usr/bin/clang++-10` | 10.0.0 | 5.613 | 3.3 |
| C++ | No | Build | `/usr/bin/g++-8` | 8.4.0 | 37.041 | 23.3 |
| C++ | No | Build | `/usr/bin/g++-9` | 9.3.0 | 42.691 | 26.8 |
| C++ | No | Build | `/usr/bin/g++-10` | 10 | 43.852 | 27.6 |
| C++ | No | Build | `/usr/bin/clang++-8` | 8.0.1 | 17.529 | 11.0 |
| C++ | No | Build | `/usr/bin/clang++-9` | 9.0.1 | 16.941 | 10.6 |
| C++ | No | Build | `/usr/bin/clang++-10` | 10.0.0 | 17.944 | 11.3 |
| C++ | Yes | Build | `/usr/bin/g++-8` | 8.4.0 | 46.511 | 18.0 |
| C++ | Yes | Build | `/usr/bin/g++-9` | 9.3.0 | 48.583 | 18.8 |
| C++ | Yes | Build | `/usr/bin/g++-10` | 10 | 54.327 | 21.0 |
| C++ | Yes | Build | `/usr/bin/clang++-8` | 8.0.1 | 17.536 | 6.8 |
| C++ | Yes | Build | `/usr/bin/clang++-9` | 9.0.1 | 18.217 | 7.1 |
| C++ | Yes | Build | `/usr/bin/clang++-10` | 10.0.0 | 23.706 | 9.2 |
| Go | No | Check | `/usr/bin/gccgo` | 10 | 2.244 | 3.5 |
| V | No | Build | `~/ware/vlang/v` | 0.1.28 | 39.465 | 24.8 |
| Zig | No | Build | `/snap/bin/zig` | 0.6.0+67273cbe7 | 8.375 | 5.3 |
| Zig | Yes | Build | `/snap/bin/zig` | 0.6.0+67273cbe7 | 10.332 | 4.0 |
| Rust | No | Check | `~/.cargo/bin/rustc` | 1.46.0-nightly | 22.479 | 34.9 |
| Rust | Yes | Check | `~/.cargo/bin/rustc` | 1.46.0-nightly | 24.034 | 14.2 |
| Rust | No | Build | `~/.cargo/bin/rustc` | 1.46.0-nightly | 68.976 | 43.3 |
| Rust | Yes | Build | `~/.cargo/bin/rustc` | 1.46.0-nightly | 42.522 | 16.5 |
| Java | No | Build | `/usr/bin/javac` | 1.8.0_171 | 7.854 | 4.9 |

This is with DMD built with LDC for an additional 15 percent drop in compilation time.

## TODO

- Add language Fortran.
- Add language Ada and do syntax checking using `-gnats`. See: https://gcc.gnu.org/onlinedocs/gcc-4.7.4/gnat_ugn_unw/Using-gcc-for-Syntax-Checking.html
