import contextlib
import io
import subprocess
import sys
import unittest

import cbench_pkg.cli


class SmokeIntegrationTestCase(unittest.TestCase):
    def test_cli_smoke_execution(self):
        """Test cbench CLI execution with minimal workload flags."""
        cmd = [
            sys.executable,
            "cbench",
            "--fc=10",
            "--fd=10",
            "--rc=1",
            "--languages=C:tcc,Python:python3,Lua:luajit,Perl:perl"
        ]
        res = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        self.assertEqual(
            res.returncode,
            0,
            f"cbench failed with exit code {res.returncode}.\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}"
        )
        # Check stderr has no python tracebacks or unhandled errors
        self.assertNotIn("Traceback (most recent call last)", res.stderr)
        self.assertNotIn("Exception:", res.stderr)

        # Check stdout contains markdown table headers and formatting
        self.assertIn("Language (Exec)", res.stdout)
        self.assertIn("|", res.stdout)
        self.assertIn("C (tcc", res.stdout)
        self.assertIn("Python (python3", res.stdout)
        self.assertIn("Lua (luajit", res.stdout)
        self.assertIn("Perl (perl", res.stdout)
    def test_programmatic_main_invocation(self):
        """Test invoking cbench_pkg.cli.main programmatically."""
        old_argv = sys.argv
        sys.argv = [
            "cbench",
            "--fc=10",
            "--fd=10",
            "--rc=1",
            "--languages=C:tcc,Lua:luajit"
        ]
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        try:
            with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stderr_capture):
                cbench_pkg.cli.main()
        except SystemExit as e:
            self.assertEqual(e.code, 0, f"cbench main exited with code {e.code}")
        finally:
            sys.argv = old_argv

        stdout = stdout_capture.getvalue()
        stderr = stderr_capture.getvalue()

        self.assertIn("Language (Exec)", stdout)
        self.assertIn("C (tcc", stdout)
        self.assertIn("Lua (luajit", stdout)


if __name__ == "__main__":
    unittest.main()
