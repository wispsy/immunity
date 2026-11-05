"""Command-line interface entry point for Immunity."""

from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""
    if argv is None:
        argv = sys.argv[1:]
    return 0


if __name__ == "__main__":
    sys.exit(main())
