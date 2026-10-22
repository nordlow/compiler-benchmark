# Repository Agent Guidelines & Documentation

## Testing & Smoke Verification
- **Smoke Integration Tests**: `tests/test_smoke.py`
  - Runs `cbench` CLI (`--fc=10 --fd=10 --rc=1`) and programmatic `cbench_pkg.cli.main` invocations.
  - Validates exit status, clean stdout (Markdown tables), clean stderr (no unhandled tracebacks), and metric bounds.
  - Run with: `python3 -m unittest tests/test_smoke.py -v`
