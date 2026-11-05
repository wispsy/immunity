"""Asynchronous Git repository management and operations."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from immunity.models import PluginLock, PluginSpec


async def run_git(
    args: Sequence[str],
    cwd: Path | str | None = None,
) -> tuple[int, str, str]:
    """Execute a git command asynchronously and return (exit_code, stdout, stderr)."""
    process = await asyncio.create_subprocess_exec(
        "git",
        *args,
        cwd=str(cwd) if cwd is not None else None,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    return (
        process.returncode or 0,
        stdout.decode("utf-8", errors="replace").strip(),
        stderr.decode("utf-8", errors="replace").strip(),
    )


async def resolve_head_commit(repo_dir: Path) -> str | None:
    """Resolve the current Git commit SHA of a repository directory."""
    code, stdout, _ = await run_git(["rev-parse", "HEAD"], cwd=repo_dir)
    return stdout if code == 0 and stdout else None


async def sync_plugin(
    spec: PluginSpec,
    cache_root: Path,
    depth: int = 1,
) -> tuple[Path | None, PluginLock | None]:
    """Clone, fetch, or update a single plugin repository asynchronously."""
    # Local directory handling
    if spec.is_local:
        local_path = (
            Path(spec.url[7:])
            if spec.url.startswith("file://")
            else Path(spec.target).expanduser()
        ).resolve()
        if not local_path.is_dir():
            return None, None
        commit = await resolve_head_commit(local_path) or "local"
        lock = PluginLock(
            name=spec.name,
            url=spec.url,
            commit=commit,
            ref=spec.ref,
            updated_at=datetime.now(timezone.utc).isoformat(),
        )
        return local_path, lock

    target_dir = cache_root / spec.cache_key

    if target_dir.exists() and (target_dir / ".git").is_dir():
        # Update existing repository
        if spec.ref:
            # Fetch ref or latest branches/tags
            fetch_code, _, _ = await run_git(
                ["fetch", "--quiet", "--tags", "origin"],
                cwd=target_dir,
            )
            # Try checking out ref
            checkout_code, _, _ = await run_git(
                ["checkout", "--quiet", spec.ref],
                cwd=target_dir,
            )
            if checkout_code == 0:
                # If on a branch, rebase against origin
                await run_git(["pull", "--quiet", "--rebase"], cwd=target_dir)
        else:
            await run_git(["pull", "--quiet", "--rebase"], cwd=target_dir)
    else:
        # Clone repository
        target_dir.parent.mkdir(parents=True, exist_ok=True)
        clone_args = ["clone", "--quiet"]
        if depth > 0 and not spec.ref:
            clone_args.extend(["--depth", str(depth)])

        if spec.ref:
            clone_args.extend(["--branch", spec.ref])

        clone_args.extend([spec.url, str(target_dir)])
        code, _, _ = await run_git(clone_args)

        # Fallback if shallow clone with --branch failed (e.g. ref was a commit SHA)
        if code != 0 and spec.ref:
            fallback_args = ["clone", "--quiet", spec.url, str(target_dir)]
            code, _, _ = await run_git(fallback_args)
            if code == 0:
                await run_git(["checkout", "--quiet", spec.ref], cwd=target_dir)

        if code != 0 or not target_dir.is_dir():
            return None, None

    commit = await resolve_head_commit(target_dir) or "unknown"
    lock = PluginLock(
        name=spec.name,
        url=spec.url,
        commit=commit,
        ref=spec.ref,
        updated_at=datetime.now(timezone.utc).isoformat(),
    )
    return target_dir, lock


async def sync_all_plugins(
    specs: Sequence[PluginSpec],
    cache_root: Path,
    depth: int = 1,
    max_concurrency: int = 12,
) -> list[tuple[PluginSpec, Path | None, PluginLock | None]]:
    """Concurrently clone or update all given plugin specifications."""
    semaphore = asyncio.Semaphore(max(1, max_concurrency))

    async def _worker(
        spec: PluginSpec,
    ) -> tuple[PluginSpec, Path | None, PluginLock | None]:
        async with semaphore:
            path, lock = await sync_plugin(spec, cache_root, depth=depth)
            return spec, path, lock

    tasks = [_worker(spec) for spec in specs]
    return await asyncio.gather(*tasks)
