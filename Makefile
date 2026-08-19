.PHONY: install run test lint demo clean

install:
	python -m pip install -e ".[dev]"

run:
	uvicorn app.main:app --reload

test:
	pytest

lint:
	ruff check .

demo:
	python scripts/seed_demo.py --count 80 --fraud-ratio 0.25

clean:
	python -c "from pathlib import Path; p=Path('data/vigiagraph.db'); p.unlink(missing_ok=True)"

