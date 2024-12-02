PYTHON=python3.10

setup:
	mkdir -p requirements # no error if exists
	mkdir -p data
	mkdir -p data/old
	mkdir -p data/new

install:
	pip install --upgrade pip-tools pip setuptools
	$(PYTHON) -m piptools compile -o requirements/main.txt pyproject.toml
	$(PYTHON) -m piptools compile --extra dev -o requirements/dev.txt pyproject.toml
	pip install -r requirements/main.txt -r requirements/dev.txt

update-deps:
	pip install --upgrade pip-tools pip setuptools
	$(PYTHON) -m piptools compile --upgrade --resolver backtracking -o requirements/main.txt pyproject.toml
	$(PYTHON) -m piptools compile --extra dev --upgrade --resolver backtracking -o requirements/dev.txt pyproject.toml

init:
	pip install --editable .
	pip install --upgrade -r requirements/main.txt  -r requirements/dev.txt

update: update-deps init

format:
	black --exclude ^/.venv .

gofetch:
	rm data/new/survey.csv
	$(PYTHON) src/fetch_answers.py