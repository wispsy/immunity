# Zsh Integration Manual

Configuring Immunity in your `.zshrc` is straightforward and requires zero runtime calls to Python during shell startup.

---

## Recommended `.zshrc` Configuration

Add the following lines to your `~/.zshrc`:

```zsh
# -----------------------------------------------------------------------------
# 1. Source statically compiled Zsh plugins
# -----------------------------------------------------------------------------
# Sourcing this single file replaces all plugin manager startup overhead.
if [[ -f ~/.zsh_plugins.zsh ]]; then
  source ~/.zsh_plugins.zsh
fi

# -----------------------------------------------------------------------------
# 2. Completion System Initialization
# -----------------------------------------------------------------------------
# Initialize compinit AFTER Immunity has configured fpath with plugin completions.
autoload -Uz compinit
if [[ -n "${ZDOTDIR:-$HOME}/.zcompdump(#qN.mh+24)" ]]; then
  compinit
else
  compinit -C
fi

# -----------------------------------------------------------------------------
# 3. Aliases
# -----------------------------------------------------------------------------
# Quick alias to recompile plugins when ~/.zsh_plugins.txt changes
alias immunity-update="immunity compile"
```

---

## Order of Execution

In Zsh, plugins that provide completions or autoloadable functions need to add their directories to the `$fpath` array **before** `compinit` is called.

Immunity guarantees this ordering in the compiled static file:
1. All plugin directories and completion folders are prepended to `fpath`.
2. Any binary directories are prepended to `path`.
3. Plugin entrypoints (`.plugin.zsh`, `init.zsh`) are sourced.

Therefore, placing `compinit` directly after sourcing `~/.zsh_plugins.zsh` ensures all completion scripts are detected.

---

## Using `zsh-defer` for Sub-Millisecond Startup

For plugins like syntax highlighting that do not need to be loaded prior to displaying the first prompt, you can use `zsh-defer`:

In `~/.zsh_plugins.txt`:
```text
romkatv/zsh-defer
zsh-users/zsh-syntax-highlighting defer:2
```

Immunity detects the `defer:2` directive and compiles the script call with `zsh-defer`:
```zsh
if (( $+functions[zsh-defer] )); then
  zsh-defer source ".../zsh-syntax-highlighting.plugin.zsh"
else
  source ".../zsh-syntax-highlighting.plugin.zsh"
fi
```
This defers high-overhead highlighting hooks until the shell is idle, yielding interactive prompts in less than 5 milliseconds.
