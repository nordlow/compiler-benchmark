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
- Generating generated/c/sample1.c took 0.394 seconds (C)
- Generating generated/c++/sample1.c++ took 0.421 seconds (C++)
- Generating generated/java/sample1.java took 0.400 seconds (Java)
- Generating generated/d/sample1.d took 0.415 seconds (D)
- Generating generated/rust/sample1.rs took 0.401 seconds (Rust)
- Generating generated/zig/sample1.zig took 0.396 seconds (Zig)
- Generating generated/go/sample1.go took 0.401 seconds (Go)
- Generating generated/v/sample1.v took 0.391 seconds (V)
- Generating generated/julia/sample1.jl took 0.404 seconds (Julia)

D:
- Checking of generated/d/sample1.d took 0.353 seconds (using "/home/per/.local/dlang/linux/bin64/dmd")
- Checking of generated/d/sample1.d took 0.388 seconds (using "/home/per/.local/ldc2-1.18.0-linux-x86_64/bin/ldmd2")

Clang:
- Checking of generated/c/sample1.c took 1.105 seconds (using "/usr/bin/clang-8")
- Checking of generated/c++/sample1.c++ took 1.410 seconds (using "/usr/bin/clang++-8")
- Speedup of D over Clang: 3.18
- Speedup of D over Clang++: 4.19
- Checking of generated/c/sample1.c took 1.230 seconds (using "/usr/bin/clang-9")
- Checking of generated/c++/sample1.c++ took 1.550 seconds (using "/usr/bin/clang++-9")
- Speedup of D over Clang: 3.49
- Speedup of D over Clang++: 4.53

GCC:
- Checking of generated/c/sample1.c took 0.380 seconds (using "/usr/bin/gcc-8")
- Checking of generated/c++/sample1.c++ took 0.936 seconds (using "/usr/bin/g++-8")
- Checking of generated/c/sample1.c took 0.404 seconds (using "/usr/bin/gcc-9")
- Checking of generated/c++/sample1.c++ took 1.048 seconds (using "/usr/bin/g++-9")
- Speedup of D over gcc-9: 1.17
- Speedup of D over g++-9: 3.09

Go:
- Checking of generated/go/sample1.go took 1.221 seconds (using "/usr/bin/gccgo")
- Speedup of D over Go: 3.48

V:
- Checking of generated/v/sample1.v took 2.893 seconds (using "/home/per/Work/v/v")
- Speedup of D over V: 8.23

Zig:
- Checking of generated/zig/sample1.zig took 4.306 seconds (using "/snap/bin/zig")
- Speedup of D over Zig: 12.20

Rust:
- Checking of generated/rust/sample1.rs took 27.590 seconds (using "/home/per/.cargo/bin/rustc")
- Speedup of D over Rust: 78.98

Java:
- Checking of generated/java/sample1.java took 4.798 seconds (using "/usr/bin/javac")
- Speedup of D over Java: 17.00
```

This is with DMD built with LDC for an additional 20 percent drop in compilation time.

## TODO

- Add language Fortran.
- Add language Ada and do syntax checking using `-gnats`. See: https://gcc.gnu.org/onlinedocs/gcc-4.7.4/gnat_ugn_unw/Using-gcc-for-Syntax-Checking.html
