test:
	poetry run python -m pytest ./tests --capture=tee-sys

lint:
	poetry run python -m pycodestyle ./src
	poetry run python -m mypy ./src

codestyle:
	poetry run python -m pydocstyle ./src
