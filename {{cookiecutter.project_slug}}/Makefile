# Load environment variables from dotenv / .env file in Bash
# https://gist.github.com/mihow/9c7f559807069a03e302605691f85572

run:
	@ docker-compose --env-file .env.development up -d; \
	trap 'docker-compose stop' INT; \
	export $$(grep -v '^#.*' .env.development | xargs); \
	hypercorn --reload --config=hypercorn.toml 'app.main:app'


lint:
	@echo
	isort --diff -c --skip-glob '*.venv' .
	@echo
	blue --check --diff --color .
	@echo
	flake8 .
	@echo
	mypy --ignore-missing-imports .


format_code:
	isort .
	blue .


test_only:
	@ docker-compose --env-file .env.testing up -d; \
	export $$(grep -v '^#.*' .env.testing | xargs); \
	pytest --cov-report term-missing --cov-report html --cov-branch \
			--cov app/; \
	docker-compose down


test: lint test_only


build:
	docker build -t {{cookiecutter.project_slug}} .
