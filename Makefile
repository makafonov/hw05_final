.env:
	@test ! -f .env && cp .env.example .env

install: .env
	poetry install --no-dev

lint:
	poetry run flake8 .

coverage:
	poetry run pytest --cov=posts --cov-report xml tests/

pytest:
	poetry run pytest -vv

unittest:
	poetry run python manage.py test

migrate:
	poetry run python manage.py migrate

start: migrate
	poetry run python manage.py runserver 0.0.0.0:8000
