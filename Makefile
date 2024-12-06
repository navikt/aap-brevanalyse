PYTHON=python3.10
VENV= .venv/bin/activate

setup:
	mkdir -p requirements # no error if exists
	mkdir -p data
	mkdir -p data/old
	mkdir -p data/new
	$(PYTHON) -m venv .venv # setup hidden venv dir

install:
	source $(VENV); \
	pip install --upgrade pip-tools pip setuptools; \
	$(PYTHON) -m piptools compile -o requirements/main.txt pyproject.toml; \
	$(PYTHON) -m piptools compile --extra dev -o requirements/dev.txt pyproject.toml; \
	pip install -r requirements/main.txt -r requirements/dev.txt

update-deps:
	source $(VENV); \
	pip install --upgrade pip-tools pip setuptools; \
	$(PYTHON) -m piptools compile --upgrade --resolver backtracking -o requirements/main.txt pyproject.toml; \
	$(PYTHON) -m piptools compile --extra dev --upgrade --resolver backtracking -o requirements/dev.txt pyproject.toml; \

init:
	source $(VENV); \
	pip install --editable .; \
	pip install --upgrade -r requirements/main.txt  -r requirements/dev.txt

update: update-deps init

format:
	source $(VENV); \
	black --exclude ^/.venv .

gofetch:
	rm data/new/survey.csv
	source $(VENV); \
	$(PYTHON) src/fetch_answers.py