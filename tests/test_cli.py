"""Tests for command-line interface."""

import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from immunity.cli import main


class TestCLI(unittest.TestCase):
    def test_version_flag(self) -> None:
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            with self.assertRaises(SystemExit) as cm:
                main(["--version"])
            self.assertEqual(cm.exception.code, 0)
            self.assertIn("immunity 0.1.0", fake_out.getvalue())

    def test_init_command(self) -> None:
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            ret = main(["init", "-o", "/path/to/compiled.zsh"])
            self.assertEqual(ret, 0)
            output = fake_out.getvalue()
            self.assertIn("source \"/path/to/compiled.zsh\"", output)
            self.assertIn("autoload -Uz compinit", output)

    def test_bundle_command_stdout(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            local_dir = Path(td) / "dummy"
            local_dir.mkdir()
            (local_dir / "dummy.plugin.zsh").touch()

            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                ret = main(["bundle", "--stdout", str(local_dir)])
                self.assertEqual(ret, 0)
                output = fake_out.getvalue()
                self.assertIn("dummy.plugin.zsh", output)

    def test_compile_missing_file_error(self) -> None:
        with patch("sys.stderr", new=io.StringIO()) as fake_err:
            ret = main(["compile", "-f", "/path/that/does/not/exist.txt"])
            self.assertEqual(ret, 1)
            self.assertIn("Specification file not found", fake_err.getvalue())


if __name__ == "__main__":
    unittest.main()
