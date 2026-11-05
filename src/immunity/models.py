"""Data models for plugin specifications and lockfiles."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class PluginSpec:
    """Represents a declared Zsh plugin specification."""

    raw: str
    target: str
    name: str
    url: str
    ref: str | None = None
    subpath: str | None = None
    kind: str = "plugin"  # "plugin", "completion", "theme", "path"
    defer: int | None = None
    pick: str | None = None

    @property
    def is_local(self) -> bool:
        """Whether the plugin references a local directory path."""
        return self.url.startswith("file://") or Path(self.target).expanduser().is_absolute()

    @property
    def cache_key(self) -> str:
        """Relative path where the plugin repository is stored in the cache."""
        if self.is_local:
            return f"local/{self.name}"

        clean_url = self.url
        for prefix in ("https://", "http://", "ssh://", "git@"):
            if clean_url.startswith(prefix):
                clean_url = clean_url[len(prefix):]
                break

        if clean_url.endswith(".git"):
            clean_url = clean_url[:-4]

        # Replace colon from scp-like syntax (github.com:user/repo -> github.com/user/repo)
        clean_url = clean_url.replace(":", "/")
        return clean_url


@dataclass(frozen=True)
class PluginLock:
    """Lock entry recording commit hash and source details."""

    name: str
    url: str
    commit: str
    ref: str | None = None
    updated_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert lock entry to a dictionary."""
        data: dict[str, Any] = {
            "name": self.name,
            "url": self.url,
            "commit": self.commit,
        }
        if self.ref is not None:
            data["ref"] = self.ref
        if self.updated_at is not None:
            data["updated_at"] = self.updated_at
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PluginLock:
        """Construct lock entry from dictionary."""
        return cls(
            name=data["name"],
            url=data["url"],
            commit=data["commit"],
            ref=data.get("ref"),
            updated_at=data.get("updated_at"),
        )
