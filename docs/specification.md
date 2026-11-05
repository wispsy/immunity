# Plugin Specification Format

Immunity reads plugin specifications line-by-line from a text file (by default `~/.zsh_plugins.txt`).

---

## Line Syntax

Each line specifies a target repository followed by optional configuration directives:

```text
TARGET [DIRECTIVE:VALUE ...]
```

- Lines starting with `#` are treated as comments and ignored.
- Blank lines and whitespace are ignored.
- Trailing comments (`# ...`) are stripped.

---

## Target Formats

### 1. GitHub Shorthand
Format: `username/repository`
```text
zsh-users/zsh-autosuggestions
```
Normalized to: `https://github.com/zsh-users/zsh-autosuggestions.git`

### 2. Branch or Tag Pinning
Append `@ref` to any target:
```text
romkatv/powerlevel10k@v1.20.0
zsh-users/zsh-syntax-highlighting@master
```

### 3. Full Git URLs
Supports HTTPS, SSH, and custom Git remotes:
```text
https://gitlab.com/user/my-plugin.git
git@github.com:company/internal-zsh-plugin.git
```

### 4. Local Directories
Prefix with `/`, `./`, `../`, or `~/`:
```text
~/Developer/custom-theme
./local-functions
```

---

## Directives

| Directive | Description | Example |
| :--- | :--- | :--- |
| `path:<subpath>` | Select a subdirectory within the repository. Useful for monorepos (e.g. Oh-My-Zsh). | `ohmyzsh/ohmyzsh path:plugins/git` |
| `kind:<type>` | Specify plugin kind: `plugin` (default), `theme`, `fpath`, or `path`. | `zsh-users/zsh-completions kind:fpath` |
| `pick:<filename>` | Explicitly choose an entrypoint script to source instead of automated heuristics. | `user/repo pick:main.zsh` |
| `defer:<level>` | Wrap script sourcing in `zsh-defer` if installed, deferring loading until after prompt display. | `zsh-users/zsh-syntax-highlighting defer:2` |
| `branch:<name>` | Alternative syntax for specifying a Git branch or tag. | `user/repo branch:stable` |
