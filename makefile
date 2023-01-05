test:
	poetry run python -m pytest ./tests --capture=tee-sys

lint:
	poetry run python -m mypy ./src
	poetry run python -m pycodestyle ./src

codestyle:
	poetry run python -m pydocstyle ./src
