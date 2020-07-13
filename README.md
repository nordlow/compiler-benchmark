# compiler-benchmark

Benchmarks compilation speeds of different combinations of languages and
compilers, currently C, C++, D, Go, Rust, V, Zig Julia and Java (via object
compilation).

Note that Julia's JIT-compiler is very memory hungry. A maximum recommended
`function-count` for Julia is 5000.

## Sample run

Just run as, for instance,

    ./benchmark --function-count=100 --function-depth=100 --run-count=5

or

    python3 benchmark --function-count=100 --function-depth=100 --run-count=5

.

This will generate code into the directory `generated` and then, for each
compiler, benchmark the standard way for that compiler to check for lexical,
syntactic and (in most cases also) semantic errors.

Note that GCC and Clang doesn't perform all semantic checks for C++ (because
it's too costly). This is in contrast to D's and Rust's compilers that perform
all of them.

## Sample output on my machine

The output on my laptop for the sample call

    ./benchmark --function-count=200 --function-depth=450 --run-count=10

results in the following output

```
Code-generation:
- Generating generated/c/linear.c took 0.494 seconds (C)
- Generating generated/c++/linear.c++ took 0.552 seconds (C++)
- Generating generated/java/linear.java took 0.448 seconds (Java)
- Generating generated/d/linear.d took 0.516 seconds (D)
- Generating generated/rust/linear.rs took 0.521 seconds (Rust)
- Generating generated/zig/linear.zig took 0.451 seconds (Zig)
- Generating generated/go/linear.go took 0.449 seconds (Go)
- Generating generated/v/linear.v took 0.446 seconds (V)
- Generating generated/julia/linear.jl took 0.453 seconds (Julia)

D:
- Check took 0.316 seconds (using "/home/per/.local/dlang/linux/bin64/dmd" version v2.092.1-beta.1-308-g3202e730d)
- Check took 0.362 seconds (using "/home/per/.local/ldc2-1.22.0-beta1-linux-x86_64/bin/ldmd2" version 1.22.0-beta1)

D-compilation:
- Compilation took 0.728 seconds (using "/home/per/.local/dlang/linux/bin64/dmd" version v2.092.1-beta.1-308-g3202e730d)
- Compilation took 7.453 seconds (using "/home/per/.local/ldc2-1.22.0-beta1-linux-x86_64/bin/ldmd2" version 1.22.0-beta1)

Clang:
- Check took 1.082 seconds (using "/usr/bin/clang-8" version 8.0.1-9)
- Check took 1.521 seconds (using "/usr/bin/clang++-8" version 8.0.1-9)
- Speedup of D over Clang: 3.40
- Speedup of D over Clang++: 4.78
- Check took 1.176 seconds (using "/usr/bin/clang-9" version 9.0.1-12)
- Check took 1.596 seconds (using "/usr/bin/clang++-9" version 9.0.1-12)
- Speedup of D over Clang: 3.80
- Speedup of D over Clang++: 5.23
- Check took 1.252 seconds (using "/usr/bin/clang-10" version 10.0.0-4ubuntu1)
- Check took 1.689 seconds (using "/usr/bin/clang++-10" version 10.0.0-4ubuntu1)
- Speedup of D over Clang: 4.00
- Speedup of D over Clang++: 5.44

GCC:
- Check took 0.333 seconds (using "/usr/bin/gcc-8" version 8.4.0-3ubuntu2))
- Check took 0.837 seconds (using "/usr/bin/g++-8" version 8.4.0-3ubuntu2))
- Check took 0.507 seconds (using "/usr/bin/gcc-9" version 9.3.0-10ubuntu2))
- Check took 1.355 seconds (using "/usr/bin/g++-9" version 9.3.0-10ubuntu2))
- Speedup of D over gcc-9: 1.61
- Speedup of D over g++-9: 4.41
- Check took 0.540 seconds (using "/usr/bin/gcc-10" version 10-20200411-0ubuntu1))
- Check took 1.525 seconds (using "/usr/bin/g++-10" version 10-20200411-0ubuntu1))
- Speedup of D over gcc-9: 1.61
- Speedup of D over g++-9: 4.41

Go:
- Check took 1.075 seconds (using "/usr/bin/gccgo" version 10-20200411-0ubuntu1))
- Speedup of D over Go: 3.40

V:
- Compilation took 19.241 seconds (using "/home/per/ware/vlang/v" version 0.1.27)
- Speedup of D over V: 60.89

Zig:
- Compilation took 4.128 seconds (using "/snap/bin/zig" version 0.6.0)
- Speedup of D over Zig: 13.16

Rust:
- Check took 11.041 seconds (using "/home/per/.cargo/bin/rustc" version 1.46.0-nightly)
- Speedup of D over Rust: 35.45

Java:
- Compilation took 4.495 seconds (using "/usr/bin/javac")
- Speedup of D over Java: 17.39
```

## Table

| Language | Templated | Oper | Exec Path | Exec Version | Time [s] | Time vs D |
| :---: | :---: | --- | :---: | :---: | :---: | :---: |
| D | No | Check | `~/.local/dlang/linux/bin64/dmd` | v2.093.0-191-g6a2716955 | 0.014 | N/A |
| D | No | Check | `~/.local/ldc2-1.22.0-linux-x86_64/bin/ldmd2` | 1.22.0 | 0.029 | N/A |
| D | Yes | Check | `~/.local/dlang/linux/bin64/dmd` | v2.093.0-191-g6a2716955 | 0.016 | N/A |
| D | Yes | Check | `~/.local/ldc2-1.22.0-linux-x86_64/bin/ldmd2` | 1.22.0 | 0.025 | N/A |
| D | No | Build | `~/.local/dlang/linux/bin64/dmd` | v2.093.0-191-g6a2716955 | 0.013 | N/A |
| D | No | Build | `~/.local/ldc2-1.22.0-linux-x86_64/bin/ldmd2` | 1.22.0 | 0.045 | N/A |
| D | Yes | Build | `~/.local/dlang/linux/bin64/dmd` | v2.093.0-191-g6a2716955 | 0.015 | N/A |
| D | Yes | Build | `~/.local/ldc2-1.22.0-linux-x86_64/bin/ldmd2` | 1.22.0 | 0.047 | N/A |
| C | No | Check | `/usr/bin/gcc-8` | 8.4.0 | 0.009 | 0.6 |
| C | No | Check | `/usr/bin/gcc-9` | 9.3.0 | 0.008 | 0.6 |
| C | No | Check | `/usr/bin/gcc-10` | 10 | 0.012 | 0.9 |
| C | No | Check | `/usr/bin/clang-8` | 8.0.1 | 0.035 | 2.5 |
| C | No | Check | `/usr/bin/clang-9` | 9.0.1 | 0.044 | 3.2 |
| C | No | Check | `/usr/bin/clang-10` | 10.0.0 | 0.024 | 1.7 |
| C | No | Build | `/usr/bin/gcc-8` | 8.4.0 | 0.066 | 4.9 |
| C | No | Build | `/usr/bin/gcc-9` | 9.3.0 | 0.072 | 5.4 |
| C | No | Build | `/usr/bin/gcc-10` | 10 | 0.072 | 5.3 |
| C | No | Build | `/usr/bin/clang-8` | 8.0.1 | 0.060 | 4.4 |
| C | No | Build | `/usr/bin/clang-9` | 9.0.1 | 0.070 | 5.2 |
| C | No | Build | `/usr/bin/clang-10` | 10.0.0 | 0.071 | 5.2 |
| C++ | No | Check | `/usr/bin/g++-8` | 8.4.0 | 0.009 | 0.7 |
| C++ | No | Check | `/usr/bin/g++-9` | 9.3.0 | 0.012 | 0.8 |
| C++ | No | Check | `/usr/bin/g++-10` | 10 | 0.012 | 0.9 |
| C++ | No | Check | `/usr/bin/clang++-8` | 8.0.1 | 0.033 | 2.4 |
| C++ | No | Check | `/usr/bin/clang++-9` | 9.0.1 | 0.041 | 2.9 |
| C++ | No | Check | `/usr/bin/clang++-10` | 10.0.0 | 0.024 | 1.7 |
| C++ | Yes | Check | `/usr/bin/g++-8` | 8.4.0 | 0.011 | 0.7 |
| C++ | Yes | Check | `/usr/bin/g++-9` | 9.3.0 | 0.013 | 0.9 |
| C++ | Yes | Check | `/usr/bin/g++-10` | 10 | 0.014 | 0.9 |
| C++ | Yes | Check | `/usr/bin/clang++-8` | 8.0.1 | 0.037 | 2.4 |
| C++ | Yes | Check | `/usr/bin/clang++-9` | 9.0.1 | 0.041 | 2.6 |
| C++ | Yes | Check | `/usr/bin/clang++-10` | 10.0.0 | 0.025 | 1.6 |
| C++ | No | Build | `/usr/bin/g++-8` | 8.4.0 | 0.078 | 5.8 |
| C++ | No | Build | `/usr/bin/g++-9` | 9.3.0 | 0.093 | 6.9 |
| C++ | No | Build | `/usr/bin/g++-10` | 10 | 0.085 | 6.3 |
| C++ | No | Build | `/usr/bin/clang++-8` | 8.0.1 | 0.070 | 5.2 |
| C++ | No | Build | `/usr/bin/clang++-9` | 9.0.1 | 0.079 | 5.8 |
| C++ | No | Build | `/usr/bin/clang++-10` | 10.0.0 | 0.081 | 6.0 |
| C++ | Yes | Build | `/usr/bin/g++-8` | 8.4.0 | 0.079 | 5.1 |
| C++ | Yes | Build | `/usr/bin/g++-9` | 9.3.0 | 0.084 | 5.5 |
| C++ | Yes | Build | `/usr/bin/g++-10` | 10 | 0.097 | 6.3 |
| C++ | Yes | Build | `/usr/bin/clang++-8` | 8.0.1 | 0.081 | 5.3 |
| C++ | Yes | Build | `/usr/bin/clang++-9` | 9.0.1 | 0.087 | 5.6 |
| C++ | Yes | Build | `/usr/bin/clang++-10` | 10.0.0 | 0.090 | 5.8 |
| Go | No | Check | `/usr/bin/gccgo` | 10 | 0.007 | 0.5 |
| V | No | Build | `~/ware/vlang/v` | 0.1.28 | 0.787 | 58.3 |
| Zig | No | Build | `/snap/bin/zig` | 0.6.0 | 0.375 | 27.8 |
| Zig | Yes | Build | `/snap/bin/zig` | 0.6.0 | 0.401 | 26.0 |
| Rust | No | Check | `~/.cargo/bin/rustc` | 1.46.0-nightly | 0.068 | 4.9 |
| Rust | Yes | Check | `~/.cargo/bin/rustc` | 1.46.0-nightly | 0.070 | 4.5 |
| Rust | No | Build | `~/.cargo/bin/rustc` | 1.46.0-nightly | 0.166 | 12.3 |
| Rust | Yes | Build | `~/.cargo/bin/rustc` | 1.46.0-nightly | 0.152 | 9.8 |
| Java | No | Build | `/usr/bin/javac` | unknown | 0.474 | 35.1 |
| Julia | No | Build | `~/.local/julia-967ac6fcb9/bin/julia` | unknown | 0.280 | 20.7 |
| Julia | Yes | Build | `~/.local/julia-967ac6fcb9/bin/julia` | unknown | 0.298 | 19.3 |

This is with DMD built with LDC for an additional 15 percent drop in compilation time.

## TODO

- Add language Fortran.
- Add language Ada and do syntax checking using `-gnats`. See: https://gcc.gnu.org/onlinedocs/gcc-4.7.4/gnat_ugn_unw/Using-gcc-for-Syntax-Checking.html
