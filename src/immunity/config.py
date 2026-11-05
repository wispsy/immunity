"""Configuration management for Immunity."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ImmunityConfig:
    """Runtime configuration paths and options for Immunity."""

    cache_dir: Path
    plugins_file: Path
    compiled_file: Path
    lock_file: Path
    clone_depth: int = 1
    max_concurrency: int = 12

    @classmethod
    def load(
        cls,
        cache_dir: Path | str | None = None,
        plugins_file: Path | str | None = None,
        compiled_file: Path | str | None = None,
        lock_file: Path | str | None = None,
        clone_depth: int = 1,
        max_concurrency: int = 12,
    ) -> ImmunityConfig:
        """Resolve configuration from parameters, environment variables, or default paths."""
        home = Path.home()

        # Cache directory resolution (respecting XDG_CACHE_HOME)
        if cache_dir is not None:
            resolved_cache = Path(cache_dir).expanduser().resolve()
        elif "IMMUNITY_CACHE_DIR" in os.environ:
            resolved_cache = Path(os.environ["IMMUNITY_CACHE_DIR"]).expanduser().resolve()
        elif "XDG_CACHE_HOME" in os.environ:
            resolved_cache = (
                Path(os.environ["XDG_CACHE_HOME"]).expanduser().resolve() / "immunity"
            )
        else:
            resolved_cache = home / ".cache" / "immunity"

        # Plugins source file resolution
        if plugins_file is not None:
            resolved_plugins = Path(plugins_file).expanduser().resolve()
        elif "IMMUNITY_PLUGINS_FILE" in os.environ:
            resolved_plugins = (
                Path(os.environ["IMMUNITY_PLUGINS_FILE"]).expanduser().resolve()
            )
        else:
            resolved_plugins = home / ".zsh_plugins.txt"

        # Compiled static output file resolution
        if compiled_file is not None:
            resolved_compiled = Path(compiled_file).expanduser().resolve()
        elif "IMMUNITY_COMPILED_FILE" in os.environ:
            resolved_compiled = (
                Path(os.environ["IMMUNITY_COMPILED_FILE"]).expanduser().resolve()
            )
        else:
            resolved_compiled = home / ".zsh_plugins.zsh"

        # Lock file resolution
        if lock_file is not None:
            resolved_lock = Path(lock_file).expanduser().resolve()
        elif "IMMUNITY_LOCK_FILE" in os.environ:
            resolved_lock = Path(os.environ["IMMUNITY_LOCK_FILE"]).expanduser().resolve()
        else:
            resolved_lock = (
                resolved_plugins.with_suffix(".lock.json")
                if resolved_plugins.name.endswith(".txt")
                else resolved_plugins.parent / f"{resolved_plugins.name}.lock.json"
            )

        env_concurrency = os.environ.get("IMMUNITY_MAX_CONCURRENCY")
        if env_concurrency is not None:
            try:
                max_concurrency = int(env_concurrency)
            except ValueError:
                pass

        return cls(
            cache_dir=resolved_cache,
            plugins_file=resolved_plugins,
            compiled_file=resolved_compiled,
            lock_file=resolved_lock,
            clone_depth=max(1, clone_depth),
            max_concurrency=max(1, max_concurrency),
        )
