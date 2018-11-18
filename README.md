# compiler-benchmark

Benchmarks compilation speeds of different combinations of languages and
compilers, currently C, C++, D, Go and Rust.

Just run as

    ./benchmark.py

or

    python3 benchmark.py

.

This will generated code into a new directory `generated/** and then benchmark
checks on that code and print the results to standard output.

## TODO

Add languages Zig and Julia.
