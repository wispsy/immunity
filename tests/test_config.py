"""Tests for configuration resolution."""

import os
import unittest
from pathlib import Path
from unittest.mock import patch

from immunity.config import ImmunityConfig


class TestConfig(unittest.TestCase):
    def test_default_config(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            cfg = ImmunityConfig.load()
            self.assertEqual(cfg.clone_depth, 1)
            self.assertEqual(cfg.max_concurrency, 12)
            self.assertEqual(cfg.plugins_file, Path.home() / ".zsh_plugins.txt")
            self.assertEqual(cfg.compiled_file, Path.home() / ".zsh_plugins.zsh")
            self.assertEqual(cfg.lock_file, Path.home() / ".zsh_plugins.lock.json")

    def test_custom_paths(self) -> None:
        custom_cache = "/tmp/custom_cache"
        custom_plugins = "/tmp/plugins.txt"
        custom_out = "/tmp/out.zsh"
        custom_lock = "/tmp/custom.lock.json"

        cfg = ImmunityConfig.load(
            cache_dir=custom_cache,
            plugins_file=custom_plugins,
            compiled_file=custom_out,
            lock_file=custom_lock,
            clone_depth=3,
            max_concurrency=4,
        )
        self.assertEqual(cfg.cache_dir, Path(custom_cache).resolve())
        self.assertEqual(cfg.plugins_file, Path(custom_plugins).resolve())
        self.assertEqual(cfg.compiled_file, Path(custom_out).resolve())
        self.assertEqual(cfg.lock_file, Path(custom_lock).resolve())
        self.assertEqual(cfg.clone_depth, 3)
        self.assertEqual(cfg.max_concurrency, 4)

    def test_env_overrides(self) -> None:
        env = {
            "IMMUNITY_CACHE_DIR": "/tmp/env_cache",
            "IMMUNITY_PLUGINS_FILE": "/tmp/env_plugins.txt",
            "IMMUNITY_COMPILED_FILE": "/tmp/env_out.zsh",
            "IMMUNITY_LOCK_FILE": "/tmp/env.lock.json",
            "IMMUNITY_MAX_CONCURRENCY": "8",
        }
        with patch.dict(os.environ, env, clear=True):
            cfg = ImmunityConfig.load()
            self.assertEqual(cfg.cache_dir, Path("/tmp/env_cache").resolve())
            self.assertEqual(cfg.plugins_file, Path("/tmp/env_plugins.txt").resolve())
            self.assertEqual(cfg.compiled_file, Path("/tmp/env_out.zsh").resolve())
            self.assertEqual(cfg.lock_file, Path("/tmp/env.lock.json").resolve())
            self.assertEqual(cfg.max_concurrency, 8)


if __name__ == "__main__":
    unittest.main()
