"""Tests for asynchronous Git client."""

import asyncio
import tempfile
import unittest
from pathlib import Path

from immunity.git import resolve_head_commit, run_git, sync_plugin
from immunity.models import PluginSpec


class TestGit(unittest.TestCase):
    def test_run_git_version(self) -> None:
        code, stdout, stderr = asyncio.run(run_git(["--version"]))
        self.assertEqual(code, 0)
        self.assertIn("git version", stdout)

    def test_local_plugin_sync(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            local_dir = Path(td).resolve()
            script = local_dir / "plugin.zsh"
            script.touch()

            # Initialize a git repo inside
            asyncio.run(run_git(["init", "--quiet"], cwd=local_dir))
            asyncio.run(run_git(["config", "user.email", "test@test.com"], cwd=local_dir))
            asyncio.run(run_git(["config", "user.name", "Test"], cwd=local_dir))
            asyncio.run(run_git(["add", "."], cwd=local_dir))
            asyncio.run(run_git(["commit", "--quiet", "-m", "init"], cwd=local_dir))

            spec = PluginSpec(
                raw=str(local_dir),
                target=str(local_dir),
                name="local-plugin",
                url=f"file://{local_dir}",
            )
            cache_root = Path(td) / "cache"
            synced_path, lock = asyncio.run(sync_plugin(spec, cache_root))

            self.assertIsNotNone(synced_path)
            self.assertEqual(synced_path, local_dir)
            self.assertIsNotNone(lock)
            assert lock is not None
            self.assertEqual(len(lock.commit), 40)


if __name__ == "__main__":
    unittest.main()
