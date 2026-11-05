"""Immunity: Ahead-of-time (AOT) compiled Zsh plugin manager."""

__version__ = "0.1.0"

from immunity.compiler import (
    compile_static_script,
    find_bin_directories,
    find_fpath_directories,
    find_init_script,
    write_compiled_script,
)
from immunity.config import ImmunityConfig
from immunity.git import resolve_head_commit, run_git, sync_all_plugins, sync_plugin
from immunity.lockfile import build_lock_data, read_lockfile, write_lockfile
from immunity.models import PluginLock, PluginSpec
from immunity.parser import parse_plugin_line, parse_plugins_file, parse_plugins_text

__all__ = [
    "__version__",
    "ImmunityConfig",
    "PluginLock",
    "PluginSpec",
    "build_lock_data",
    "compile_static_script",
    "find_bin_directories",
    "find_fpath_directories",
    "find_init_script",
    "parse_plugin_line",
    "parse_plugins_file",
    "parse_plugins_text",
    "read_lockfile",
    "resolve_head_commit",
    "run_git",
    "sync_all_plugins",
    "sync_plugin",
    "write_compiled_script",
    "write_lockfile",
]
