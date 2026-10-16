"""Shared helpers used by multiple language modules."""

from ..types import _no_limits


def _make_dim_limiter(lang_name: str, max_total: int, capped_dim: int,
                      reason: str = "compiler scaling limits"):
    def _limiter(args):
        if args.function_count * args.function_depth > max_total:
            msg = (f"Warning: Capping {lang_name} function count/depth from {args.function_count}x{args.function_depth} "
                   f"to {capped_dim}x{capped_dim} due to {reason}")
            args.function_count = capped_dim
            args.function_depth = capped_dim
            return [msg]
        return []
    return _limiter


# Swift / Crystal / TypeScript capping limits (each language module wires its own).
_SWIFT_MAX_TOTAL_FUNCS = 10_000
_SWIFT_CAPPED_DIM = 100
_CRYSTAL_MAX_TOTAL_FUNCS = 10_000
_CRYSTAL_CAPPED_DIM = 100
_TYPESCRIPT_MAX_TOTAL_FUNCS = 10_000
_TYPESCRIPT_CAPPED_DIM = 100

swift_limits = _make_dim_limiter("Swift", _SWIFT_MAX_TOTAL_FUNCS, _SWIFT_CAPPED_DIM,
                                 "swiftc constraint solver limits")
crystal_limits = _make_dim_limiter("Crystal", _CRYSTAL_MAX_TOTAL_FUNCS, _CRYSTAL_CAPPED_DIM,
                                   "global type inference limits")
typescript_limits = _make_dim_limiter("TypeScript", _TYPESCRIPT_MAX_TOTAL_FUNCS,
                                      _TYPESCRIPT_CAPPED_DIM,
                                      "V8 heap and AST scaling limits")

# Clojure / F# / R capping limits.
_CLOJURE_MAX_TOTAL_FUNCS = 10_000
_CLOJURE_CAPPED_DIM = 100
_FSHARP_MAX_TOTAL_FUNCS = 10_000
_FSHARP_CAPPED_DIM = 100
_R_MAX_TOTAL_FUNCS = 10_000
_R_CAPPED_DIM = 100

clojure_limits = _make_dim_limiter("Clojure", _CLOJURE_MAX_TOTAL_FUNCS, _CLOJURE_CAPPED_DIM,
                                   "JVM class and method size scaling limits")
fsharp_limits = _make_dim_limiter("F#", _FSHARP_MAX_TOTAL_FUNCS, _FSHARP_CAPPED_DIM,
                                  "dotnet fsi type checker and AST scaling limits")
r_limits = _make_dim_limiter("R", _R_MAX_TOTAL_FUNCS, _R_CAPPED_DIM,
                             "R parser and bytecode compiler limits")


def _ocaml_julia_limits(args):
    # These scale poorly on deeply nested functions with large synthetic function counts.
    max_total = 10_000
    capped_dim = 200
    if args.function_count * args.function_depth >= max_total:
        msg = (f"Warning: Capping function count/depth from {args.function_count}x{args.function_depth} "
               f"to {capped_dim}x{capped_dim} due to nested call-tree scaling limits")
        args.function_count = capped_dim
        args.function_depth = capped_dim
        return [msg]
    return []
