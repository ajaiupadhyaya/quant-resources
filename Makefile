.PHONY: toc build serve sync export-reqs clean

toc:
	uv run python scripts/generate_toc.py

build: toc
	uv run jupyter-book build --site

serve: toc
	uv run jupyter-book start

sync:
	uv sync --all-extras

export-reqs:
	uv export --all-extras --no-dev --no-emit-project --no-hashes -o requirements.txt

clean:
	uv run jupyter-book clean
	rm -rf _build
