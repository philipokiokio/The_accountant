

PYTHON = venv/bin/python
PIP = venv/bin/pip
BLACK = venv/bin/python -m black
RUFF = venv/bin/python -m ruff 
MESSAGE = "The Acccountant Table Migrations"
STEP = 1


venv : 
	python3 -m venv venv
	
activate :
	source /venv/bin/activate

install :
	pip install -r requirements.txt 

# integration-test:
# 	pytest --cov=accountant tests/integration_test

unit-test:
	pytest --cov=accountant tests/unit_tests

# all-test:
# 	pytest --cov=accountant tests


local-migration:
	alembic -c local_alembic.ini revision -m "$(MESSAGE)" --autogenerate
local-migrate:
	alembic -c local_alembic.ini upgrade heads
local-migrate-down:
	alembic -c local_alembic.ini downgrade -"$(STEP)"
local-head:
	alembic -c local_alembic.ini heads
root_server:
	uvicorn accountant.root.app:app --reload --port=7200
rq_scheduler: 
	rqscheduler


rq_worker:
	rq worker --with-scheduler

celery_jobs:
	celery -A groundible.job_manager.celery_manager worker -B --loglevel=INFO


format : 
	$(BLACK) --preview ./accountant

standard:
	$(RUFF) check ./accountant --ignore=E731,E712


env_db_migration: 
	sh db_migration.sh
