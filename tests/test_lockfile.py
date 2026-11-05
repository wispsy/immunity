"""Tests for lockfile reader and writer."""

import tempfile
import unittest
from pathlib import Path

from immunity.lockfile import build_lock_data, read_lockfile, write_lockfile
from immunity.models import PluginLock, PluginSpec


class TestLockfile(unittest.TestCase):
    def test_build_and_write_read_lockfile(self) -> None:
        spec = PluginSpec(
            raw="zsh-users/zsh-autosuggestions@v0.7.0",
            target="zsh-users/zsh-autosuggestions@v0.7.0",
            name="zsh-autosuggestions",
            url="https://github.com/zsh-users/zsh-autosuggestions.git",
            ref="v0.7.0",
        )
        lock = PluginLock(
            name=spec.name,
            url=spec.url,
            commit="abcdef1234567890",
            ref=spec.ref,
            updated_at="2026-11-04T12:00:00Z",
        )

        results = [(spec, Path("/tmp/fake"), lock)]
        lock_data = build_lock_data(results)

        self.assertEqual(lock_data["version"], 1)
        self.assertIn("plugins", lock_data)
        self.assertIn(spec.target, lock_data["plugins"])
        self.assertEqual(lock_data["plugins"][spec.target]["commit"], "abcdef1234567890")

        with tempfile.NamedTemporaryFile("w+", delete=False) as tf:
            temp_path = Path(tf.name)

        try:
            write_lockfile(temp_path, lock_data)
            loaded = read_lockfile(temp_path)
            self.assertIsNotNone(loaded)
            assert loaded is not None
            self.assertEqual(loaded["version"], 1)
            self.assertEqual(
                loaded["plugins"][spec.target]["commit"],
                "abcdef1234567890",
            )
        finally:
            temp_path.unlink()


if __name__ == "__main__":
    unittest.main()
