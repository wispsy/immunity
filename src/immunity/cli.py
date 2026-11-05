"""Command-line interface for Immunity."""

from __future__ import annotations

import argparse
import asyncio
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Sequence

from immunity import __version__
from immunity.compiler import compile_static_script, write_compiled_script
from immunity.config import ImmunityConfig
from immunity.git import sync_all_plugins
from immunity.lockfile import build_lock_data, write_lockfile
from immunity.models import PluginSpec
from immunity.parser import parse_plugins_file, parse_plugins_text


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="immunity",
        description="Ahead-of-time (AOT) compiled Zsh plugin manager in Python.",
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # compile
    compile_p = subparsers.add_parser(
        "compile",
        help="Compile plugins into a static .zsh script",
    )
    _add_common_options(compile_p)
    compile_p.add_argument(
        "--no-lock",
        action="store_true",
        help="Do not write or update the lockfile",
    )

    # update
    update_p = subparsers.add_parser(
        "update",
        help="Fetch latest changes for all plugins and recompile",
    )
    _add_common_options(update_p)

    # bundle
    bundle_p = subparsers.add_parser(
        "bundle",
        help="Fetch and compile ad-hoc plugin specifications",
    )
    bundle_p.add_argument(
        "plugins",
        nargs="*",
        help="Plugin targets (e.g. zsh-users/zsh-autosuggestions)",
    )
    _add_common_options(bundle_p, include_file=False)
    bundle_p.add_argument(
        "--stdout",
        action="store_true",
        help="Output compiled script directly to stdout",
    )

    # lock
    lock_p = subparsers.add_parser(
        "lock",
        help="Inspect and write reproducible lockfile",
    )
    _add_common_options(lock_p, include_output=False)

    # clean
    clean_p = subparsers.add_parser(
        "clean",
        help="Remove cached plugins not listed in the specification",
    )
    clean_p.add_argument(
        "-c", "--cache-dir",
        type=str,
        help="Custom cache directory",
    )
    clean_p.add_argument(
        "-f", "--file",
        type=str,
        help="Plugin specification file",
    )
    clean_p.add_argument(
        "-y", "--yes",
        action="store_true",
        help="Skip confirmation prompt",
    )

    # init
    init_p = subparsers.add_parser(
        "init",
        help="Print recommended .zshrc integration snippet",
    )
    init_p.add_argument(
        "-o", "--output",
        type=str,
        help="Path to compiled script to reference",
    )

    return parser


def _add_common_options(
    parser: argparse.ArgumentParser,
    include_file: bool = True,
    include_output: bool = True,
) -> None:
    if include_file:
        parser.add_argument(
            "-f", "--file",
            type=str,
            help="Path to plugins specification file (default: ~/.zsh_plugins.txt)",
        )
    if include_output:
        parser.add_argument(
            "-o", "--output",
            type=str,
            help="Path to compiled static script output (default: ~/.zsh_plugins.zsh)",
        )
    parser.add_argument(
        "-c", "--cache-dir",
        type=str,
        help="Directory to cache cloned repositories (default: ~/.cache/immunity)",
    )
    parser.add_argument(
        "--lock-file",
        type=str,
        help="Path to lockfile (default: ~/.zsh_plugins.lock.json)",
    )
    parser.add_argument(
        "-j", "--jobs",
        type=int,
        default=12,
        help="Maximum concurrent network tasks (default: 12)",
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=1,
        help="Git clone depth (default: 1)",
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress informational console output",
    )


async def _run_compile(
    config: ImmunityConfig,
    specs: list[PluginSpec],
    write_lock: bool = True,
    quiet: bool = False,
    stdout: bool = False,
) -> int:
    start_time = time.perf_counter()

    if not specs:
        if not quiet and not stdout:
            print("No plugins specified.")
        return 0

    if not quiet and not stdout:
        print(f"Immunity: Synchronizing {len(specs)} plugin(s)...")

    results = await sync_all_plugins(
        specs,
        cache_root=config.cache_dir,
        depth=config.clone_depth,
        max_concurrency=config.max_concurrency,
    )

    compiled_code = compile_static_script(results)

    if stdout:
        sys.stdout.write(compiled_code)
    else:
        write_compiled_script(config.compiled_file, compiled_code)

    if write_lock and not stdout:
        lock_data = build_lock_data(results)
        write_lockfile(config.lock_file, lock_data)

    duration = time.perf_counter() - start_time
    if not quiet and not stdout:
        successful = sum(1 for _, path, _ in results if path is not None)
        print(
            f"Immunity: Compiled {successful}/{len(specs)} plugin(s) to "
            f"{config.compiled_file} in {duration:.2f}s."
        )

    return 0


def _handle_clean(config: ImmunityConfig, specs: list[PluginSpec], yes: bool) -> int:
    if not config.cache_dir.is_dir():
        print("Cache directory does not exist. Nothing to clean.")
        return 0

    active_keys = {spec.cache_key for spec in specs}
    to_delete: list[Path] = []

    for root, dirs, _ in os.walk(config.cache_dir):
        root_path = Path(root)
        if (root_path / ".git").is_dir():
            rel_key = root_path.relative_to(config.cache_dir).as_posix()
            if rel_key not in active_keys:
                to_delete.append(root_path)
            dirs.clear()

    if not to_delete:
        print("No orphaned cached plugins found.")
        return 0

    print(f"Found {len(to_delete)} orphaned plugin directory(ies):")
    for d in to_delete:
        print(f"  - {d}")

    if not yes:
        reply = input("Delete these directories? [y/N]: ").strip().lower()
        if reply not in ("y", "yes"):
            print("Aborted.")
            return 0

    for d in to_delete:
        shutil.rmtree(d, ignore_errors=True)
    print("Orphaned plugins removed.")
    return 0


def _handle_init(output_file: str | None) -> int:
    target_path = output_file or "~/.zsh_plugins.zsh"
    snippet = f"""# -----------------------------------------------------------------------------
# Immunity Zsh Integration
# Add the following lines to your ~/.zshrc:
# -----------------------------------------------------------------------------

# 1. Source statically compiled plugins if present (zero Python runtime overhead)
if [[ -f "{target_path}" ]]; then
  source "{target_path}"
fi

# 2. Initialize completion system after fpath has been populated
autoload -Uz compinit && compinit

# 3. Helpful alias for recompiling when plugins change
alias immunity-update="immunity compile"
"""
    print(snippet)
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """CLI execution entrypoint."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        # Default action when called without subcommand: compile
        args.command = "compile"
        args.file = None
        args.output = None
        args.cache_dir = None
        args.lock_file = None
        args.jobs = 12
        args.depth = 1
        args.quiet = False
        args.no_lock = False

    if args.command == "init":
        return _handle_init(getattr(args, "output", None))

    config = ImmunityConfig.load(
        cache_dir=getattr(args, "cache_dir", None),
        plugins_file=getattr(args, "file", None),
        compiled_file=getattr(args, "output", None),
        lock_file=getattr(args, "lock_file", None),
        clone_depth=getattr(args, "depth", 1),
        max_concurrency=getattr(args, "jobs", 12),
    )

    if args.command == "clean":
        specs = parse_plugins_file(config.plugins_file)
        return _handle_clean(config, specs, getattr(args, "yes", False))

    if args.command == "bundle":
        raw_plugins = args.plugins or []
        if not raw_plugins and not sys.stdin.isatty():
            content = sys.stdin.read()
            specs = parse_plugins_text(content)
        else:
            specs = parse_plugins_text("\n".join(raw_plugins))

        stdout = getattr(args, "stdout", False)
        return asyncio.run(
            _run_compile(
                config,
                specs,
                write_lock=not getattr(args, "no_lock", False),
                quiet=getattr(args, "quiet", False),
                stdout=stdout,
            )
        )

    if args.command in ("compile", "update", "lock"):
        if not config.plugins_file.is_file():
            print(
                f"Error: Specification file not found: {config.plugins_file}\n"
                f"Create this file with a list of plugins (e.g. zsh-users/zsh-autosuggestions) "
                f"or specify --file PATH.",
                file=sys.stderr,
            )
            return 1

        specs = parse_plugins_file(config.plugins_file)

        if args.command == "lock":
            # Sync to inspect commits and write lockfile only
            results = asyncio.run(
                sync_all_plugins(
                    specs,
                    cache_root=config.cache_dir,
                    depth=config.clone_depth,
                    max_concurrency=config.max_concurrency,
                )
            )
            lock_data = build_lock_data(results)
            write_lockfile(config.lock_file, lock_data)
            if not getattr(args, "quiet", False):
                print(f"Immunity: Updated lockfile at {config.lock_file}")
            return 0

        write_lock = not getattr(args, "no_lock", False)
        return asyncio.run(
            _run_compile(
                config,
                specs,
                write_lock=write_lock,
                quiet=getattr(args, "quiet", False),
                stdout=False,
            )
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
