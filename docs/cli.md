# Command-Line Interface Reference

The `immunity` executable provides several subcommands for managing and compiling Zsh plugins.

---

## Global Options

- `-h, --help`: Display help information for any command or subcommand.
- `-v, --version`: Display the current version of Immunity.

---

## `immunity compile`

Compile plugins defined in your specification file into a static `.zsh` script and generate an updated lockfile.

```bash
immunity compile [options]
```

### Options:
- `-f, --file PATH`: Path to plugins specification file (default: `~/.zsh_plugins.txt` or `$IMMUNITY_PLUGINS_FILE`).
- `-o, --output PATH`: Path to compiled static script (default: `~/.zsh_plugins.zsh` or `$IMMUNITY_COMPILED_FILE`).
- `-c, --cache-dir DIR`: Directory for cloned repositories (default: `~/.cache/immunity` or `$XDG_CACHE_HOME/immunity`).
- `--lock-file PATH`: Path to output lockfile (default: `~/.zsh_plugins.lock.json`).
- `--no-lock`: Skip lockfile creation.
- `-j, --jobs CONCURRENCY`: Maximum concurrent Git tasks (default: 12).
- `--depth DEPTH`: Git clone depth (default: 1).
- `-q, --quiet`: Suppress informational output.

---

## `immunity update`

Fetch the latest commits for all plugins and recompile the static script and lockfile.

```bash
immunity update [options]
```

Accepts the same configuration flags as `compile`.

---

## `immunity bundle`

Ad-hoc compilation of plugins passed as command-line arguments or via standard input.

```bash
# Via arguments
immunity bundle zsh-users/zsh-autosuggestions zsh-users/zsh-syntax-highlighting

# Via standard input
cat my_plugins.txt | immunity bundle --stdout
```

### Options:
- `--stdout`: Output compiled script directly to standard output instead of writing to disk.

---

## `immunity lock`

Inspect existing plugin repositories and update `~/.zsh_plugins.lock.json` with commit SHAs without recompiling the static shell script.

```bash
immunity lock [-f PATH] [--lock-file PATH]
```

---

## `immunity clean`

Inspect the cache directory and identify any repository folders that are no longer listed in your specification file.

```bash
immunity clean [-y]
```

### Options:
- `-y, --yes`: Automatically confirm deletion of orphaned plugin directories.

---

## `immunity init`

Print the recommended `.zshrc` shell integration snippet.

```bash
immunity init [-o PATH]
```
