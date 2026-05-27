# quant-resources

Jupyter notebooks from [Quant Guild Library](https://github.com/romanmichaelpaolucci/Quant-Guild-Library) for personal study. Folder names match the original lecture structure (`2025 Video Lectures/`, `2026 Video Lectures/`).

**Attribution:** Notebooks are © Quant Guild / Roman Paolucci. This repo is an unofficial mirror containing notebooks only (no lecture link files or other assets). For videos and updates, use the [official library](https://github.com/romanmichaelpaolucci/Quant-Guild-Library) and [Quant Guild](https://quantguild.com).

**Contents:** 84+ `.ipynb` files — notebooks only, no `YouTube_Video_Link` text files.

## Study site (Jupyter Book)

This repo builds a browsable **Jupyter Book** site from all lecture notebooks.

| Action | Command |
|--------|---------|
| Install deps | `uv sync --all-extras` |
| Regenerate sidebar TOC | `uv run python scripts/generate_toc.py` |
| Build static site | `make build` or `uv run jupyter-book build --site` |
| Preview locally | `make serve` or `uv run jupyter-book start` |

After `make build`, open `_build/site/public/index.html` in a browser (or use `make serve`).

### GitHub Pages

On push to `main`, [.github/workflows/deploy-book.yml](.github/workflows/deploy-book.yml) builds and deploys the site. Enable **Settings → Pages → Build and deployment → GitHub Actions** if it is not already on.

### Binder (run notebooks in the cloud)

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/ajaiupadhyaya/quant-resources/main?labpath=intro.md)

Uses `requirements.txt` (from `make export-reqs`) and [binder/postBuild](binder/postBuild) for NLTK/spaCy data.

**Note:** Some notebooks reference images or packages not in this mirror (`qfin`, lecture PNGs). Those cells may fail until you add assets from the official library.

## Project layout

```
intro.md              # Home page
myst.yml              # Jupyter Book / MyST config
toc.yml               # Auto-generated table of contents
scripts/generate_toc.py
pyproject.toml        # uv dependencies
```

When you add notebooks, rerun `uv run python scripts/generate_toc.py` before building.
