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

    ./benchmark --function-count=50000 --run-count=5

results in the following output

```
- Generating generated/c/sample1.c took 0.412 seconds (C)
- Generating generated/c++/sample1.c++ took 0.452 seconds (C++)
- Generating generated/java/sample1.java took 0.447 seconds (Java)
- Generating generated/d/sample1.d took 0.456 seconds (D)
- Generating generated/rust/sample1.rs took 0.418 seconds (Rust)
- Generating generated/zig/sample1.zig took 0.395 seconds (Zig)
- Generating generated/go/sample1.go took 0.402 seconds (Go)
- Generating generated/v/sample1.v took 0.412 seconds (V)
- Generating generated/julia/sample1.jl took 0.397 seconds (Julia)

D:
- Checking of generated/d/sample1.d took 0.479 seconds (using "/usr/bin/dmd")
- Checking of generated/d/sample1.d took 0.377 seconds (using "/home/per/.local/ldc2-1.18.0-linux-x86_64/bin/ldmd2")

Clang:
- Checking of generated/c/sample1.c took 1.130 seconds (using "/usr/bin/clang-8")
- Checking of generated/c++/sample1.c++ took 1.485 seconds (using "/usr/bin/clang++-8")
- Speedup of D over Clang: 2.99
- Speedup of D over Clang++: 3.93
- Checking of generated/c/sample1.c took 1.247 seconds (using "/usr/bin/clang-9")
- Checking of generated/c++/sample1.c++ took 1.635 seconds (using "/usr/bin/clang++-9")
- Speedup of D over Clang: 3.30
- Speedup of D over Clang++: 4.33

GCC:
- Checking of generated/c/sample1.c took 0.399 seconds (using "/usr/bin/gcc-8")
- Checking of generated/c++/sample1.c++ took 0.945 seconds (using "/usr/bin/g++-8")
- Checking of generated/c/sample1.c took 0.424 seconds (using "/usr/bin/gcc-9")
- Checking of generated/c++/sample1.c++ took 1.059 seconds (using "/usr/bin/g++-9")
- Speedup of D over gcc-9: 1.12
- Speedup of D over g++-9: 2.80

Go:
- Checking of generated/go/sample1.go took 1.213 seconds (using "/usr/bin/gccgo")
- Speedup of D over Go: 3.21

Java:
stderr: b'generated/java/sample1.java:45003: error: code too large\n    public static void main(String args[]) {\n                       ^\ngenerated/java/sample1.java:1: error: too many constants\nclass HelloWorld {\n^\n2 errors\n'
- Checking of generated/java/sample1.java took 5.456 seconds (using "/usr/bin/javac")
- Speedup of D over Java: 14.45

Rust:
- Checking of generated/rust/sample1.rs took 27.244 seconds (using "/home/per/.cargo/bin/rustc")
- Speedup of D over Rust: 72.17

V:
stderr: b'warning: generated/v/sample1.v:1:6: the following imports were never used: \n * os\n'
- Checking of generated/v/sample1.v took 2.413 seconds (using "/home/per/Work/v/v")
- Speedup of D over V: 6.39

Zig:
- Checking of generated/zig/sample1.zig took 4.212 seconds (using "/snap/bin/zig")
- Speedup of D over Zig: 11.16
```

## TODO

Add language Fortran.
