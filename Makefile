lint:
	@echo
	isort --diff -c --skip-glob '*.venv' {{cookiecutter.project_slug}}
	@echo
	blue --check --diff --color {{cookiecutter.project_slug}}
	@echo
	flake8 {{cookiecutter.project_slug}}
	@echo
	mypy --ignore-missing-imports {{cookiecutter.project_slug}}


format_code:
	isort {{cookiecutter.project_slug}}
	blue {{cookiecutter.project_slug}}
