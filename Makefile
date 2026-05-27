.PHONY: polish toc build serve sync export-reqs clean

polish:
	uv run python scripts/polish_notebooks.py

toc: polish
	uv run python scripts/generate_toc.py

build: toc
	BASE_URL=/quant-resources uv run jupyter-book build --site --html
	uv run python scripts/postprocess_html.py

serve: toc
	uv run jupyter-book start

sync:
	uv sync --all-extras

export-reqs:
	uv export --all-extras --no-dev --no-emit-project --no-hashes -o requirements.txt

clean:
	uv run jupyter-book clean
	rm -rf _build _publish
