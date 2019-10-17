# compiler-benchmark

Benchmarks compilation speeds of different combinations of languages and
compilers, currently C, C++, D, Go, Rust, V, Zig and Julia.

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

    ./benchmark --function-count=50000 --run-count=5

results in the following output

```
Code-generation:
- Generating generated/c/sample1.c took 0.422 seconds (C)
- Generating generated/c++/sample1.c++ took 0.447 seconds (C++)
- Generating generated/d/sample1.d took 0.447 seconds (D)
- Generating generated/rust/sample1.rs took 0.428 seconds (Rust)
- Generating generated/zig/sample1.zig took 0.423 seconds (Zig)
- Generating generated/go/sample1.go took 0.430 seconds (Go)
- Generating generated/v/sample1.v took 0.419 seconds (V)
- Generating generated/julia/sample1.jl took 0.422 seconds (Julia)

D:
- Checking of generated/d/sample1.d took 0.502 seconds (using "/usr/bin/dmd")
- Checking of generated/d/sample1.d took 0.405 seconds (using "/home/per/.local/ldc2-1.18.0-linux-x86_64/bin/ldmd2")

Clang:
- Checking of generated/c/sample1.c took 1.160 seconds (using "/usr/bin/clang-8")
- Checking of generated/c++/sample1.c++ took 1.522 seconds (using "/usr/bin/clang++-8")
- Speedup of D over Clang: 2.86
- Speedup of D over Clang++: 3.76
- Checking of generated/c/sample1.c took 1.323 seconds (using "/usr/bin/clang-9")
- Checking of generated/c++/sample1.c++ took 1.722 seconds (using "/usr/bin/clang++-9")
- Speedup of D over Clang: 3.27
- Speedup of D over Clang++: 4.25

GCC:
- Checking of generated/c/sample1.c took 0.431 seconds (using "/usr/bin/gcc-8")
- Checking of generated/c++/sample1.c++ took 1.017 seconds (using "/usr/bin/g++-8")
- Checking of generated/c/sample1.c took 0.451 seconds (using "/usr/bin/gcc-9")
- Checking of generated/c++/sample1.c++ took 1.132 seconds (using "/usr/bin/g++-9")
- Speedup of D over gcc-9: 1.11
- Speedup of D over g++-9: 2.79

Go:
- Checking of generated/go/sample1.go took 1.305 seconds (using "/usr/bin/gccgo")
- Speedup of D over Go: 3.22

Rust:
- Checking of generated/rust/sample1.rs took 31.508 seconds (using "/home/per/.cargo/bin/rustc")
- Speedup of D over Rust: 77.80

Zig:
- Checking of generated/zig/sample1.zig took 4.616 seconds (using "/snap/bin/zig")
- Speedup of D over Zig: 11.40

```

## TODO

Add languages Java.
