# Implementation Plan: Immunity v0.1.0 (Prototype / Experimental)

Immunity is an ahead-of-time (AOT) compiled Zsh plugin manager implemented in Python. It is designed to combine the concurrency and dependency modeling capabilities of Python with zero-overhead shell startup speeds.

---

## 1. Architectural Overview & Design Principles

### 1.1 The AOT Compilation Philosophy
Executing interpreted runtimes during interactive shell startup introduces 50–150ms of latency per invocation. Immunity avoids this by strictly separating the **build/compilation phase** from the **execution phase**:

```
[User Plugins Spec]
       │
       ▼
 [Immunity CLI] ──(async clone/fetch)──▶ [Local Plugin Cache (~/.cache/immunity)]
       │
       ▼ (AOT Compiler & Entrypoint Discovery)
 [Static Shell Script (~/.zsh_plugins.zsh)]
       │
       ▼ (Sourced directly by ~/.zshrc)
  [Instant Zsh Shell Startup (Raw I/O Speed)]
```

- **Compilation Phase (Python)**: Fetches and updates repositories concurrently using `asyncio`, parses plugin manifests, resolves entrypoints according to Zsh standards, indexes completions into `fpath`, and renders an optimized static `.zsh` script.
- **Execution Phase (Native Zsh)**: Interactive shells source the compiled `.zsh` artifact directly via raw filesystem I/O without launching Python.

### 1.2 Core Specifications
- **Runtime Target**: Python >= 3.10 (tested through 3.14). Pure standard library implementation with zero external runtime dependencies.
- **Packaging Standard**: Modern PEP 517 / PEP 621 compliant packaging using `uv_build`.
- **Concurrency**: Asynchronous subprocess execution for parallel Git operations (clone, fetch, checkout, rev-parse).
- **Standards Compliance**: Full adherence to the Zsh Plugin Standard (ZSH-PLUG), supporting standard plugins, completions, themes, and path sanitization.

---

## 2. Milestone Breakdown for v0.1.0

### Milestone 1: Packaging & Core Domain Models (`feat(core)`)
- Structure project under `src/immunity/`.
- Establish configuration defaults (`~/.cache/immunity`, `~/.zsh_plugins.txt`, `~/.zsh_plugins.zsh`, `~/.zsh_plugins.lock.json`).
- Implement specification parsing supporting:
  - Repository shorthands (`user/repo` -> `https://github.com/user/repo.git`).
  - Full Git URLs (`https://`, `ssh://`, `git@`).
  - Branch, tag, and commit pinning syntax (`user/repo@v1.2.0`, `user/repo@main`, `user/repo:commit`).
  - Comment handling (`#`) and inline directive flags (`path:subdir`, `kind:theme`, `defer:2`).

### Milestone 2: Asynchronous Git Engine & Lockfile Subsystem (`feat(git)`)
- Asynchronous Git client wrapping `asyncio.subprocess`.
- Concurrent cloning using shallow depth (`--depth=1` by default) with automatic unshallow/tag capabilities when pinning requires.
- Concurrent repository update mechanism with fast-forward/rebase fallback.
- Commit hash resolution and deterministic lockfile generation (`plugins.lock.json`).

### Milestone 3: Plugin Parser & AOT Static Compiler (`feat(compiler)`)
- Zsh standard entrypoint discovery rules:
  1. Explicitly configured scripts via directives.
  2. `<plugin-name>.plugin.zsh`
  3. `<plugin-name>.zsh`
  4. `<plugin-name>.zsh-theme`
  5. `init.zsh`
  6. Single top-level `*.zsh` fallback.
- Completion discovery: detection of `_functions` or completion directories and prepending to `fpath`.
- Theme separation and environment isolation.
- Static file compilation generating clean, sourceable Zsh syntax with compilation header and execution guards.

### Milestone 4: Command Line Interface (`feat(cli)`)
- Unified CLI entry point: `immunity`.
- Subcommands:
  - `compile`: Read plugin specifications and output compiled static Zsh script.
  - `update`: Fetch updates for all configured plugins and recompile.
  - `bundle`: Ad-hoc compilation of plugins passed directly via arguments or standard input.
  - `lock`: Inspect git repositories and emit a reproducible `plugins.lock.json`.
  - `clean`: Prune cached repositories that are no longer referenced in configuration.
  - `init`: Emit recommended `.zshrc` integration snippets.
- ANSI-formatted console feedback with progress indicators and error reporting.

### Milestone 5: Automated Testing Suite (`test`)
- Unit tests for configuration parsing, plugin shorthand resolution, and entrypoint discovery.
- Async mock tests for Git operations and concurrency boundaries.
- End-to-end integration tests using local mock Git repositories verifying static compilation and lockfile generation.
- CLI execution tests verifying exit codes and stdout/stderr behavior.

### Milestone 6: Documentation (`docs`)
- Comprehensive user manual in `docs/`:
  - `docs/index.md`: Architecture and getting started.
  - `docs/cli.md`: Command-line interface reference.
  - `docs/specification.md`: Plugin specification format, directives, and pinning.
  - `docs/zsh-integration.md`: `.zshrc` integration patterns and performance optimization.
- Top-level `README.md` with badges, installation instructions, and quickstart examples.

### Milestone 7: Continuous Integration & Release Pipelines (`ci`)
- GitHub Actions CI workflow in `.github/workflows/workflow.yaml`:
  - Matrix testing across Python versions.
  - Linting, style checks, and packaging validation.
  - Full test execution.
- GitHub Actions PyPI release workflow in `.github/workflows/release.yaml`:
  - Triggered on published GitHub release.
  - Environment configured to `pypi`.
  - OIDC trusted publishing using `pypa/gh-action-pypi-publish`.

---

## 3. Branching, Review, and Commit Strategy
- Every issue maps to a single dedicated feature branch:
  - `feat/core-domain`
  - `feat/async-git`
  - `feat/static-compiler`
  - `feat/cli-interface`
  - `test/test-suite`
  - `docs/documentation`
  - `ci/workflows-and-release`
- Each branch is squash-merged into `main` with Conventional Commits titles.
- Release tag `v0.1.0` cut upon completion to trigger automated PyPI deployment.
