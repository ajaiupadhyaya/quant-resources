#!/usr/bin/env python3
"""Post-process MyST HTML build for GitHub Pages."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD_HTML = ROOT / "_build" / "html"

THEME_SCRIPT_OLD = """  const savedTheme = localStorage.getItem("myst:theme");
  const theme = window.matchMedia("(prefers-color-scheme: light)").matches ? 'light' : 'dark';
  const classes = document.documentElement.classList;
  const hasAnyTheme = classes.contains('light') || classes.contains('dark');
  if (!hasAnyTheme) classes.add(savedTheme ?? theme);
"""

THEME_SCRIPT_NEW = """  window.addEventListener('load', () => {
    const savedTheme = localStorage.getItem("myst:theme");
    const theme = window.matchMedia("(prefers-color-scheme: light)").matches ? 'light' : 'dark';
    const classes = document.documentElement.classList;
    const hasAnyTheme = classes.contains('light') || classes.contains('dark');
    if (!hasAnyTheme) classes.add(savedTheme ?? theme);
  }, { once: true });
"""


def patch_html_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text
    if THEME_SCRIPT_OLD in text:
        text = text.replace(THEME_SCRIPT_OLD, THEME_SCRIPT_NEW)
    path.write_text(text, encoding="utf-8")
    return text != original


def verify_assets(base: Path, base_url: str = "/quant-resources") -> list[str]:
    missing: list[str] = []
    prefix = base_url.rstrip("/")
    for html_path in base.rglob("*.html"):
        content = html_path.read_text(encoding="utf-8", errors="ignore")
        for ref in re.findall(r'(?:href|src)="(' + re.escape(prefix) + r'/[^"]+)"', content):
            rel = ref[len(prefix) + 1 :].split("?")[0]
            if not (base / rel).exists():
                missing.append(f"{html_path.relative_to(base)} -> {rel}")
    return missing


def main() -> int:
    if not BUILD_HTML.is_dir():
        print(f"Missing build output: {BUILD_HTML}", file=sys.stderr)
        return 1

    (BUILD_HTML / ".nojekyll").touch()

    patched = sum(patch_html_file(p) for p in BUILD_HTML.rglob("*.html"))

    missing = verify_assets(BUILD_HTML)
    if missing:
        print("Missing assets referenced in HTML:", file=sys.stderr)
        for item in missing[:20]:
            print(f"  {item}", file=sys.stderr)
        if len(missing) > 20:
            print(f"  ... and {len(missing) - 20} more", file=sys.stderr)
        return 1

    print(f"Post-processed {BUILD_HTML.relative_to(ROOT)}: .nojekyll, {patched} HTML files patched")
    return 0


if __name__ == "__main__":
    sys.exit(main())
