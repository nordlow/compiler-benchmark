# compiler-benchmark

Benchmarks compilation speeds of different combinations of languages and
compilers, currently C, C++, D, Go and Rust.

Just run as

    ./benchmark.py

or

    python3 benchmark.py

.

This will generate code into the directory `generated` and then, for each
compiler, benchmark the standard way for that compiler to check for lexical,
syntactic and (in most cases also) semantic errors.

Note that GCC and Clang doesn't perform all semantic checks for C++ (because
it's too costly). This is in contrast to D's and Rust's compilers that perform
all of them.

## TODO

Add languages Zig, Julia, Java.
