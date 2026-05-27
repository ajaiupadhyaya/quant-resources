---
title: Quant Resources
short_title: Home
---

# Quant Resources

Interactive study library of **Quant Guild** lecture notebooks ([official library](https://github.com/romanmichaelpaolucci/Quant-Guild-Library), [Quant Guild](https://quantguild.com)).

Use the sidebar to browse **2025** and **2026** video lecture topics. Each page is a notebook with explanations, math, and (where saved) plot outputs.

## How to use this site

- **Read here** — Browse rendered notebooks in your browser (no setup).
- **Run locally** — Clone the repo, then:

  ```bash
  uv sync
  uv run jupyter lab
  ```

- **Run in the cloud** — Use the **Open in Binder** button (top right) to launch a free Jupyter session. First launch can take several minutes.

## Attribution

Notebooks are © **Quant Guild / Roman Paolucci**. This repository is an unofficial personal study mirror (notebooks only).

## Maintainer

Site built with [Jupyter Book](https://jupyterbook.org) (MyST). Table of contents is regenerated with:

```bash
uv run python scripts/generate_toc.py
uv run jupyter-book build --site
```
