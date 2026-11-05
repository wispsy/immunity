# Installation Guide

Immunity requires Python 3.10 or later and Git.

---

## Recommended: Install via `uv`

If you use `uv`, install Immunity as a standalone CLI tool:

```bash
uv tool install immunity
```

To update to the latest release:

```bash
uv tool upgrade immunity
```

---

## Install via `pip` or `pipx`

Using `pipx` (recommended for isolated CLI tools):

```bash
pipx install immunity
```

Using standard user-level `pip`:

```bash
pip install --user immunity
```

---

## From Source (Development)

Clone the repository and install locally:

```bash
git clone https://github.com/wispsy/immunity.git
cd immunity
uv sync
```

You can run commands directly using:

```bash
uv run immunity --help
```
