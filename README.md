# compiler-benchmark

Benchmarks compilation speeds of different combinations of languages and
compilers, currently C, C++, D, Go, Rust, V, Zig Julia and Java (via object
compilation).

Note that Julia's JIT-compiler is very memory hungry. A maximum recommended
`function-count` for Julia is 5000.

## Sample run

Just run as, for instance,

    ./benchmark --function-count=10000 --run-count=5

or

    python3 benchmark --function-count=10000 --run-count=5

.

This will generate code into the directory `generated` and then, for each
compiler, benchmark the standard way for that compiler to check for lexical,
syntactic and (in most cases also) semantic errors.

Note that GCC and Clang doesn't perform all semantic checks for C++ (because
it's too costly). This is in contrast to D's and Rust's compilers that perform
all of them.

## Sample output on my machine

The output on my laptop for the sample call

    ./benchmark --function-count=45000 --run-count=10

results in the following output

```
Code-generation:
- Generating generated/c/sample1.c took 0.393 seconds (C)
- Generating generated/c++/sample1.c++ took 0.416 seconds (C++)
- Generating generated/java/sample1.java took 0.405 seconds (Java)
- Generating generated/d/sample1.d took 0.416 seconds (D)
- Generating generated/rust/sample1.rs took 0.394 seconds (Rust)
- Generating generated/zig/sample1.zig took 0.395 seconds (Zig)
- Generating generated/go/sample1.go took 0.396 seconds (Go)
- Generating generated/v/sample1.v took 0.389 seconds (V)
- Generating generated/julia/sample1.jl took 0.392 seconds (Julia)

D:
- Checking of generated/d/sample1.d took 0.351 seconds (using "/home/per/.local/dlang/linux/bin64/dmd")
- Checking of generated/d/sample1.d took 0.388 seconds (using "/home/per/.local/ldc2-1.18.0-linux-x86_64/bin/ldmd2")

Clang:
- Checking of generated/c/sample1.c took 1.093 seconds (using "/usr/bin/clang-8")
- Checking of generated/c++/sample1.c++ took 1.397 seconds (using "/usr/bin/clang++-8")
- Speedup of D over Clang: 3.17
- Speedup of D over Clang++: 4.05
- Checking of generated/c/sample1.c took 1.226 seconds (using "/usr/bin/clang-9")
- Checking of generated/c++/sample1.c++ took 1.569 seconds (using "/usr/bin/clang++-9")
- Speedup of D over Clang: 3.46
- Speedup of D over Clang++: 4.69

GCC:
- Checking of generated/c/sample1.c took 0.387 seconds (using "/usr/bin/gcc-8")
- Checking of generated/c++/sample1.c++ took 0.930 seconds (using "/usr/bin/g++-8")
- Checking of generated/c/sample1.c took 0.409 seconds (using "/usr/bin/gcc-9")
- Checking of generated/c++/sample1.c++ took 1.055 seconds (using "/usr/bin/g++-9")
- Speedup of D over gcc-9: 1.16
- Speedup of D over g++-9: 2.97

Go:
- Checking of generated/go/sample1.go took 1.214 seconds (using "/usr/bin/gccgo")
- Speedup of D over Go: 3.45

Java:
- Checking of generated/java/sample1.java took 5.102 seconds (using "/usr/bin/javac")
- Speedup of D over Java: 15.59

Rust:
- Checking of generated/rust/sample1.rs took 27.509 seconds (using "/home/per/.cargo/bin/rustc")
- Speedup of D over Rust: 77.34

V:
- Checking of generated/v/sample1.v took 2.416 seconds (using "/home/per/Work/v/v")
- Speedup of D over V: 6.83

Zig:
- Checking of generated/zig/sample1.zig took 4.306 seconds (using "/snap/bin/zig")
- Speedup of D over Zig: 12.18
```

## TODO

- Add language Fortran.
- Add language Ada and do syntax checking using `-gnats`. See: https://gcc.gnu.org/onlinedocs/gcc-4.7.4/gnat_ugn_unw/Using-gcc-for-Syntax-Checking.html
