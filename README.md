# compiler-benchmark

Benchmarks compilation speeds of different combinations of languages and
compilers, currently C, C++, D, Go, Rust, V, Zig and Julia.

Just run as, for instance,

    ./benchmark --function-count=10000 --run-counnt=5

or

    python3 benchmark

.

This will generate code into the directory `generated` and then, for each
compiler, benchmark the standard way for that compiler to check for lexical,
syntactic and (in most cases also) semantic errors.

Note that GCC and Clang doesn't perform all semantic checks for C++ (because
it's too costly). This is in contrast to D's and Rust's compilers that perform
all of them.

## Sample output on my machine



## TODO

Add languages Java.
