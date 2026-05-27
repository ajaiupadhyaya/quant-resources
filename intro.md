---
title: Quant Guild Study Library
short_title: Home
---

# Quant Guild Study Library

Structured notes and code from [Quant Guild](https://quantguild.com) video lectures—organized for reading and review, not social promotion.

```{note}
**Attribution.** Notebooks are © Quant Guild / Roman Paolucci. This site is an unofficial study mirror. For videos and the full asset library, see the [official Quant Guild Library](https://github.com/romanmichaelpaolucci/Quant-Guild-Library).
```

## Browse

Choose a year in the sidebar, then a lecture. Each page is one notebook: theory, derivations, and figures (outputs are shown; code is available below each section).

| Year | Focus |
|------|--------|
| **2025 Lectures** | Foundations—options, stochastic calculus, simulation, ML |
| **2026 Lectures** | Processes, risk-neutral pricing, portfolio methods |

## Run notebooks

**Locally** (recommended for long runs):

```bash
uv sync --all-extras
uv run jupyter lab
```

**In the browser** — use **Open in Binder** on any page (first launch may take several minutes).

## Site maintenance

```bash
make polish   # rebuild _publish/ from source notebooks
make build    # polish + TOC + static site
```
