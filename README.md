# compiler-benchmark

Benchmarks compilation speeds of different combinations of languages and
compilers, currently C, C++, D, Go and Rust.

Just run as

    ./benchmark.py

or

    python3 benchmark.py

.

This will generate code into the directory `generated` and then perform
benchmarks of the standard way for a compiler to check that generated for
lexical, syntactic and in most case also semantic checks. Notice that GCC and
Clang doesn't perform all semantic checks (because it's too costly). This is in
contrast to D's and Rust's compilers that performs all of them.

## TODO

Add languages Zig, Julia, Java.
