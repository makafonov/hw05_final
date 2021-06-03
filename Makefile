install:
	poetry install

lint:
	poetry run flake8 yatube

coverage:
	poetry run pytest --cov=yatube --cov-report xml tests/

pytest:
	poetry run pytest -vv

unittest:
	poetry run python manage.py test

migrate:
	poetry run python manage.py migrate

start: migrate
	poetry run python manage.py runserver 0.0.0.0:8000
