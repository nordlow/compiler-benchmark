"""Per-language benchmark modules.

Each module is a self-contained block: runner(s) + a `register_language(...)`
call. Drop a new module here to add a language; the engine discovers it through
the `LANGUAGES` registry in `cbench_pkg.types`.
"""
