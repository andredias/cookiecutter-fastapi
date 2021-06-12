POSTGRESQL_RUNNING = $(shell docker ps | grep postgres-development)
REDIS_RUNNING = $(shell docker ps | grep redis-development)


run: start_postgres start_redis
	@ trap 'echo "Stopping postgres..."; docker stop -t 0 postgres-development redis-development' INT; \
	ENV=development hypercorn --reload --config=hypercorn.toml 'app.main:app'


lint:
	@echo
	isort --diff -c --skip-glob '*.venv' .
	@echo
	blue --check --diff --color .
	@echo
	flake8 .
	@echo
	mypy --ignore-missing-imports --install-types .


format_code:
	isort .
	blue .


test_only:
	pytest -svx --cov-report term-missing --cov-report html --cov-branch \
			--cov app/


test: lint test_only


start_postgres:
	@ if [ -z "$(POSTGRESQL_RUNNING)" ]; then \
		echo 'Starting PostgreSQL...'; \
		docker run -d --rm -p 5432:5432 -e POSTGRES_DB={{cookiecutter.project_slug}} \
			-e POSTGRES_PASSWORD=development_1234 --name postgres-development \
			postgres:alpine; \
	fi


start_redis:
	@ if [ -z "$(REDIS_RUNNING)" ]; then \
		echo 'Starting Redis...'; \
		docker run -d --rm -p 6379:6379  \
			--name redis-development \
			redis:alpine; \
	fi



build:
	docker build -t {{cookiecutter.project_slug}} .
