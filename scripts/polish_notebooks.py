#!/usr/bin/env python3
"""
Build publication-ready notebook copies under _publish/.

Strips Quant Guild video-site boilerplate (promo links, widget CSS cells,
duplicate outline blocks) and normalizes headings — without modifying originals.
"""

from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLISH_ROOT = ROOT / "_publish"
SOURCE_ROOTS = ("2025 Video Lectures", "2026 Video Lectures")

# MyST / Jupyter Book cell tags (https://mystmd.org/guide/notebooks-with-markdown)
TAG_REMOVE = "remove-cell"
TAG_HIDE_INPUT = "hide-input"

EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001FAFF"
    "\U00002600-\U000027BF"
    "\U00002300-\U000023FF"
    "]+",
    flags=re.UNICODE,
)

BOILERPLATE_MARKERS = (
    "related quant guild videos",
    "▶️ related",
    "master your quantitative skills",
    "visit the quant guild library",
    "interactive brokers",
    "join the quant guild discord",
    "quant guild discord",
    "algorithmic trading](https://www.interactivebrokers",
)

WIDGET_STYLE_MARKERS = (
    "cell-output-ipywidget-background",
    "--jp-widgets-color",
    "--vscode-editor-foreground",
)

MD_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
HTML_IMAGE_RE = re.compile(
    r"<img\b[^>]*\bsrc=[\"']([^\"']+)[\"'][^>]*/?>",
    re.IGNORECASE,
)
MATH_INLINE_RE = re.compile(r"(?<!\$)\$(?!\$)([^$]+?)\$(?!\$)")
MATH_DISPLAY_RE = re.compile(r"\$\$([^$]+?)\$\$", re.DOTALL)

# Map Quant Guild "checklist" emojis in math to LaTeX-safe symbols
EMOJI_MATH_REPLACEMENTS = (
    ("✅", r"\checkmark"),
    ("❌", r"?"),
)


def folder_number(name: str) -> int:
    match = re.match(r"^(\d+)\.", name)
    return int(match.group(1)) if match else 99_999


def folder_title(name: str) -> str:
    match = re.match(r"^\d+\.\s*(.+)", name)
    return match.group(1).strip() if match else name


def clean_text(text: str) -> str:
    text = EMOJI_RE.sub("", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def resolve_asset_path(asset_dir: Path, ref: str) -> Path:
    ref = ref.strip().split("?")[0].split("#")[0]
    path = Path(ref)
    if path.is_absolute():
        return path
    return (asset_dir / path).resolve()


def asset_exists(asset_dir: Path, ref: str) -> bool:
    if ref.startswith(("http://", "https://", "data:")):
        return True
    return resolve_asset_path(asset_dir, ref).is_file()


def fix_math_segment(body: str) -> str:
    for emoji, latex in EMOJI_MATH_REPLACEMENTS:
        body = body.replace(emoji, latex)
    body = EMOJI_RE.sub("", body)
    # % comments out the rest of a LaTeX line — escape when used as a percent sign
    body = re.sub(r"(?<!\\)%", r"\\%", body)
    return body


def fix_latex_math(text: str) -> str:
    text = MATH_DISPLAY_RE.sub(lambda m: f"$${fix_math_segment(m.group(1))}$$", text)
    text = MATH_INLINE_RE.sub(lambda m: f"${fix_math_segment(m.group(1))}$", text)
    return text


def strip_missing_images(text: str, asset_dir: Path) -> str:
    """Drop markdown/HTML image references when the file is not in the lecture folder."""

    def md_repl(match: re.Match[str]) -> str:
        ref = match.group(2).strip()
        if asset_exists(asset_dir, ref):
            return match.group(0)
        return ""

    def html_repl(match: re.Match[str]) -> str:
        ref = match.group(1).strip()
        if asset_exists(asset_dir, ref):
            return match.group(0)
        return ""

    text = HTML_IMAGE_RE.sub(html_repl, text)
    text = MD_IMAGE_RE.sub(md_repl, text)
    return text


def cell_source(cell: dict[str, Any]) -> str:
    src = cell.get("source", "")
    if isinstance(src, list):
        return "".join(src)
    return str(src)


def set_cell_source(cell: dict[str, Any], text: str) -> None:
    text = text if text.endswith("\n") else text + "\n"
    cell["source"] = text.splitlines(keepends=True)


def add_tag(cell: dict[str, Any], tag: str) -> None:
    meta = cell.setdefault("metadata", {})
    tags = meta.setdefault("tags", [])
    if tag not in tags:
        tags.append(tag)


def is_underscore_line(line: str) -> bool:
    stripped = line.strip()
    return len(stripped) > 30 and set(stripped) <= {"_", "-"}


def is_boilerplate_line(line: str) -> bool:
    low = line.lower()
    return any(marker in low for marker in BOILERPLATE_MARKERS)


def is_widget_style_cell(source: str) -> bool:
    if "%%html" not in source:
        return False
    return any(marker in source for marker in WIDGET_STYLE_MARKERS)


def is_sections_outline_cell(source: str) -> bool:
    first_line = source.split("\n", 1)[0].strip().lower()
    return "sections" in first_line and source.count("\n") > 3


def is_hr_only_cell(source: str) -> bool:
    return source.strip() in ("---", "***", "___", "----")


def extract_heading_title(source: str) -> str | None:
    for line in source.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            title = re.sub(r"^#+\s*", "", stripped)
            title = clean_text(title)
            if title:
                return title
    return None


def strip_boilerplate_markdown(source: str, fallback_title: str) -> str | None:
    """Return a clean opening markdown cell, or None to drop the cell."""
    title = extract_heading_title(source) or fallback_title
    kept_lines: list[str] = []
    in_related_block = False

    for line in source.splitlines():
        low = line.lower().strip()
        if "related quant guild videos" in low or low.startswith("##### ▶️"):
            in_related_block = True
            continue
        if in_related_block:
            if line.strip().startswith("- [") or line.strip() == "":
                continue
            if line.strip() in ("---", ""):
                continue
            in_related_block = False
        if is_boilerplate_line(line) or is_underscore_line(line):
            continue
        if low.startswith("##### [") and ("quantguild" in low or "interactivebrokers" in low):
            continue
        kept_lines.append(line)

    body_lines = [
        ln
        for ln in kept_lines
        if ln.strip()
        and not is_underscore_line(ln)
        and ln.strip() not in ("---", "***", "___")
    ]
    # If only headings remain, use title page only
    content_lines = [ln for ln in body_lines if not ln.strip().startswith("#")]
    if not content_lines:
        return f"# {title}\n"

    out: list[str] = [f"# {title}", ""]
    for line in body_lines:
        if line.strip().startswith("#"):
            if any(m in line.lower() for m in BOILERPLATE_MARKERS):
                continue
            if clean_text(line.lstrip("#").strip()) == title:
                continue
            continue
        out.append(line)
    text = "\n".join(out).strip()
    return (text + "\n") if text else f"# {title}\n"


def normalize_markdown_headings(source: str) -> str:
    """Demote emoji-heavy ### openers; clean emoji from headings."""
    lines: list[str] = []
    for line in source.splitlines():
        match = re.match(r"^(#{1,6})\s+(.*)$", line)
        if match:
            hashes, text = match.groups()
            text = clean_text(text)
            if text:
                lines.append(f"{hashes} {text}")
            continue
        lines.append(line)
    return "\n".join(lines)


def polish_markdown(source: str, asset_dir: Path) -> str:
    source = strip_missing_images(source, asset_dir)
    source = fix_latex_math(source)
    source = normalize_markdown_headings(source)
    lines = [
        ln
        for ln in source.splitlines()
        if ln.strip() not in ("#", "##", "###", "<div>", "</div>")
    ]
    return "\n".join(lines)


def polish_cells(
    cells: list[dict[str, Any]],
    lecture_title: str,
    lecture_num: int | None,
    asset_dir: Path,
) -> list[dict[str, Any]]:
    polished: list[dict[str, Any]] = []
    seen_title = False

    for cell in cells:
        source = cell_source(cell)
        ctype = cell.get("cell_type")

        if ctype == "code" and is_widget_style_cell(source):
            tagged = json.loads(json.dumps(cell))
            add_tag(tagged, TAG_REMOVE)
            polished.append(tagged)
            continue

        if ctype == "markdown" and is_hr_only_cell(source):
            continue

        if ctype == "markdown" and is_sections_outline_cell(source):
            tagged = json.loads(json.dumps(cell))
            add_tag(tagged, TAG_REMOVE)
            polished.append(tagged)
            continue

        if ctype == "markdown" and not seen_title:
            cleaned = strip_boilerplate_markdown(source, lecture_title)
            if cleaned is None:
                continue
            seen_title = True
            new_cell = json.loads(json.dumps(cell))
            set_cell_source(new_cell, polish_markdown(cleaned, asset_dir))
            polished.append(new_cell)
            continue

        if ctype == "markdown":
            new_cell = json.loads(json.dumps(cell))
            set_cell_source(new_cell, polish_markdown(source, asset_dir))
            polished.append(new_cell)
            continue

        if ctype == "code":
            new_cell = json.loads(json.dumps(cell))
            # Hide empty setup cells (style placeholders already removed)
            if not source.strip():
                add_tag(new_cell, TAG_REMOVE)
            polished.append(new_cell)
            continue

        polished.append(cell)

    if not seen_title:
        polished.insert(
            0,
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": f"# {lecture_title}\n",
            },
        )

    return polished


def polish_notebook(src: Path, dst: Path) -> None:
    data = json.loads(src.read_text(encoding="utf-8"))
    folder_name = src.parent.name
    lecture_title = folder_title(folder_name)
    lecture_num = folder_number(folder_name) if folder_number(folder_name) < 99_999 else None

    meta = data.setdefault("metadata", {})
    myst = meta.setdefault("myst", {})
    myst["title"] = lecture_title
    if lecture_num is not None:
        myst["subtitle"] = f"Lecture {lecture_num}"

    cells = polish_cells(data.get("cells", []), lecture_title, lecture_num, src.parent)
    data["cells"] = cells

    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def sync_publish_tree() -> int:
    if PUBLISH_ROOT.exists():
        shutil.rmtree(PUBLISH_ROOT)
    PUBLISH_ROOT.mkdir(parents=True)

    count = 0
    for root_name in SOURCE_ROOTS:
        src_root = ROOT / root_name
        if not src_root.is_dir():
            continue
        for src in sorted(src_root.rglob("*.ipynb")):
            if ".ipynb_checkpoints" in src.parts:
                continue
            rel = src.relative_to(ROOT)
            dst = PUBLISH_ROOT / rel
            polish_notebook(src, dst)
            count += 1
    return count


def main() -> int:
    count = sync_publish_tree()
    print(f"Polished {count} notebooks → {PUBLISH_ROOT.relative_to(ROOT)}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
