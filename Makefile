manage = poetry run python src/manage.py

.env:
	@test ! -f .env && cp .env.example .env

install: .env
	@poetry install --no-dev

lint:
	@poetry run flake8 src/

coverage:
	@poetry run pytest --cov=posts --cov-report xml tests/

pytest:
	@poetry run pytest

unittest:
	@$(manage) test src

migrate:
	@$(manage) migrate

run:
	@$(manage) runserver
