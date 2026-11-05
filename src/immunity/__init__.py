"""Immunity: Ahead-of-time (AOT) compiled Zsh plugin manager."""

__version__ = "0.1.0"

from immunity.config import ImmunityConfig
from immunity.models import PluginLock, PluginSpec
from immunity.parser import parse_plugin_line, parse_plugins_file, parse_plugins_text

__all__ = [
    "__version__",
    "ImmunityConfig",
    "PluginLock",
    "PluginSpec",
    "parse_plugin_line",
    "parse_plugins_file",
    "parse_plugins_text",
]
