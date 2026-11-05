"""Parser for plugins.txt specification files."""

from __future__ import annotations

import shlex
from pathlib import Path

from immunity.models import PluginSpec


def _normalize_repo_target(raw_target: str) -> tuple[str, str, str | None]:
    """Parse raw target into (name, url, ref).

    Handles:
      - 'user/repo'
      - 'user/repo@tag-or-branch'
      - 'https://github.com/user/repo.git'
      - 'git@github.com:user/repo.git'
      - '/local/path'
    """
    target = raw_target.strip()
    ref: str | None = None

    if "@" in target and not target.startswith("git@"):
        target_part, ref_part = target.split("@", 1)
        target = target_part.strip()
        ref = ref_part.strip() or None

    # Local path
    if target.startswith(("/", "./", "../", "~/")):
        expanded = Path(target).expanduser()
        return expanded.name, f"file://{expanded.resolve()}", ref

    # Full git URL
    if any(target.startswith(prefix) for prefix in ("https://", "http://", "ssh://", "git://", "git@")):
        url = target
        if url.endswith(".git"):
            name = url[:-4].rstrip("/").split("/")[-1].split(":")[-1]
        else:
            name = url.rstrip("/").split("/")[-1].split(":")[-1]
        return name, url, ref

    # Shorthand github repository (e.g., zsh-users/zsh-autosuggestions)
    parts = target.strip("/").split("/")
    name = parts[-1]
    url = f"https://github.com/{target}.git"
    return name, url, ref


def parse_plugin_line(line: str) -> PluginSpec | None:
    """Parse a single line of plugin declaration."""
    clean_line = line.strip()
    if not clean_line or clean_line.startswith("#"):
        return None

    # Strip trailing comments if unquoted
    tokens = shlex.split(clean_line, comments=True)
    if not tokens:
        return None

    target_token = tokens[0]
    name, url, ref = _normalize_repo_target(target_token)

    subpath: str | None = None
    kind = "plugin"
    defer: int | None = None
    pick: str | None = None

    for token in tokens[1:]:
        if ":" in token:
            key, val = token.split(":", 1)
            key = key.lower().strip()
            val = val.strip()
            if key == "path":
                subpath = val
            elif key == "kind":
                kind = val.lower()
            elif key == "defer":
                try:
                    defer = int(val)
                except ValueError:
                    pass
            elif key in ("pick", "source"):
                pick = val
            elif key in ("branch", "tag", "ref"):
                ref = val

    return PluginSpec(
        raw=clean_line,
        target=target_token,
        name=name,
        url=url,
        ref=ref,
        subpath=subpath,
        kind=kind,
        defer=defer,
        pick=pick,
    )


def parse_plugins_text(text: str) -> list[PluginSpec]:
    """Parse multiple plugin specifications from a text block."""
    specs: list[PluginSpec] = []
    for line in text.splitlines():
        spec = parse_plugin_line(line)
        if spec is not None:
            specs.append(spec)
    return specs


def parse_plugins_file(path: Path | str) -> list[PluginSpec]:
    """Parse plugin specifications from a file."""
    file_path = Path(path).expanduser().resolve()
    if not file_path.is_file():
        return []
    content = file_path.read_text(encoding="utf-8")
    return parse_plugins_text(content)
