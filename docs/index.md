# Immunity Documentation

Welcome to the **Immunity** documentation.

Immunity is an ahead-of-time (AOT) compiled Zsh plugin manager implemented in Python.

---

## The Ahead-of-Time (AOT) Compilation Paradigm

Traditional shell plugin managers suffer from a fundamental trade-off:

1. **Native Zsh managers (e.g. Oh-My-Zsh, Antigen)**: Written entirely in shell script, but parsing complex dependency structures, network synchronization, and multi-threading in shell script is complex and slow.
2. **External runtime managers**: Written in languages like Python, Ruby, or Node.js. If an external interpreter is invoked every time a terminal tab opens, startup latency increases by 50ms to 200ms per shell session.

### How Immunity Solves This

Immunity uses an **Ahead-of-Time compilation model**:

```
[~/.zsh_plugins.txt]
        │
        ▼ (immunity compile: async git clone + heuristics)
[~/.cache/immunity]
        │
        ▼ (static compiler)
[~/.zsh_plugins.zsh]  ◄──── Sourced directly by ~/.zshrc (0ms Python penalty)
```

1. **Compilation Phase (Python)**: Immunity runs only when you want to install or update plugins. It uses Python's asynchronous I/O (`asyncio`) to clone and update repositories in parallel, discovers completions, and writes an optimized, static `.zsh` script.
2. **Runtime Phase (Zsh)**: Every time you launch a terminal, your `.zshrc` simply sources the statically compiled `.zsh_plugins.zsh` file using raw native filesystem I/O. Shell startup is instantaneous.

---

## Design Principles

- **Zero Runtime Dependencies**: Uses Python's standard library exclusively.
- **Maximum Concurrency**: Parallel Git operations prevent slow network stalls.
- **Standards Compliance**: Adheres to the Zsh Plugin Standard (ZSH-PLUG).
- **Reproducibility**: Commit SHAs are recorded in a deterministic JSON lockfile.
