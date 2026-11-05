# Immunity

[![PyPI version](https://img.shields.io/pypi/v/immunity.svg)](https://pypi.org/project/immunity/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)

**Immunity** is an ultra-fast, ahead-of-time (AOT) compiled Zsh plugin manager written in Python.

It combines Python's rich concurrency ecosystem (`asyncio`) for parallel cloning, updates, and lock resolution with zero shell startup overhead. Instead of executing Python each time an interactive shell launches, Immunity compiles your plugins into a single, clean static `.zsh` script sourced directly by your shell at raw filesystem I/O speeds.

---

## Key Features

- **Ahead-of-Time (AOT) Compilation**: 0ms Python startup penalty during shell load. Sourcing a compiled `.zsh` file takes < 2ms.
- **Concurrent Git Operations**: Parallel shallow cloning and rebase pulls via `asyncio`.
- **Standards Compliant**: Full support for Zsh plugin standards (`.plugin.zsh`, `init.zsh`, themes, autoload/completions directories).
- **Deterministic Lockfiles**: Generates `plugins.lock.json` recording commit SHAs for 100% reproducible shell setups across machines.
- **Zero Runtime Dependencies**: Written entirely with Python's standard library. No third-party packages required.
- **Flexible Directives**: Supports branch/tag pinning (`@v1.0.0`), subpaths (`path:subdir`), deferral (`defer:2`), custom entrypoints (`pick:init.zsh`), and completions (`kind:fpath`).

---

## Quickstart

### 1. Installation

Install via `pip` or `uv`:

```bash
uv tool install immunity
# or
pip install --user immunity
```

### 2. Define Plugins (`~/.zsh_plugins.txt`)

Create `~/.zsh_plugins.txt` with your desired plugins:

```text
# Syntax highlighting & suggestions
zsh-users/zsh-syntax-highlighting
zsh-users/zsh-autosuggestions
zsh-users/zsh-history-substring-search

# Prompts & Themes
romkatv/powerlevel10k@v1.20.0

# Completions
zsh-users/zsh-completions kind:fpath
```

### 3. Compile

Run the Immunity compiler:

```bash
immunity compile
```

This concurrently fetches any missing plugins, indexes completions into `fpath`, discovers entrypoint scripts, and outputs `~/.zsh_plugins.zsh` along with `~/.zsh_plugins.lock.json`.

### 4. Wire up `.zshrc`

Add the following to your `~/.zshrc`:

```zsh
# Source statically compiled plugins if present
if [[ -f ~/.zsh_plugins.zsh ]]; then
  source ~/.zsh_plugins.zsh
fi

# Initialize completions after fpath has been configured
autoload -Uz compinit && compinit

# Alias for easy recompilation
alias immunity-update="immunity compile"
```

You can also run `immunity init` to generate this template automatically.

---

## Command Reference

| Command | Description |
| :--- | :--- |
| `immunity compile` | Compile configured plugins into static `.zsh` file and lockfile. |
| `immunity update` | Pull latest updates for all plugins and recompile static file. |
| `immunity bundle <repos...>` | Ad-hoc compilation of plugins passed as arguments or via stdin. |
| `immunity lock` | Generate or refresh `plugins.lock.json` with commit SHAs. |
| `immunity clean` | Remove cached plugins no longer referenced in your specification. |
| `immunity init` | Print shell integration snippet for `~/.zshrc`. |

---

## Directives & Syntax

In your plugins file:

```text
# Shorthand GitHub repo
zsh-users/zsh-autosuggestions

# Pin specific branch or tag
romkatv/powerlevel10k@v1.20.0

# Subdirectory inside repository
ohmyzsh/ohmyzsh path:plugins/git

# Add to fpath without sourcing an init script
zsh-users/zsh-completions kind:fpath

# Explicit entrypoint file
zsh-users/zsh-history-substring-search pick:zsh-history-substring-search.zsh

# Deferred loading with zsh-defer
zsh-users/zsh-syntax-highlighting defer:2
```

---

## Documentation

Full documentation is available in the `docs/` folder:

- [Architecture & Overview](docs/index.md)
- [Installation Guide](docs/installation.md)
- [CLI Reference](docs/cli.md)
- [Specification Format & Directives](docs/specification.md)
- [Zsh Integration Manual](docs/zsh-integration.md)

---

## License

MIT © [Wispsy](https://github.com/wispsy)
