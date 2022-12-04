run-all: ingestor dashboard

database:
	docker compose --env-file .env.sh up --build -d postgres

ingestor:
	docker compose --env-file .env.sh up --build -d ingestor

dashboard:
	docker compose --env-file .env.sh up --build -d dashboard

lint:
	flake8 --extend-exclude='venv/' --max-line-length=120 .

format:
	black .

# ci: format type lint pytest



# down:
#     docker compose --env-file env down 

# sh:
#     docker exec -ti loader bash

# run-etl:
#     docker exec loader python load_user_data.py

# warehouse:
#     docker exec -ti warehouse psql postgres://sdeuser:sdepassword1234@localhost:5432/warehouse

# pytest:
#     docker exec loader pytest -p no:warnings -v /opt/sde/test

# format:
#     docker exec loader python -m black -S --line-length 79 /opt/sde
#     docker exec loader isort /opt/sde

# type:
#     docker exec loader mypy --ignore-missing-imports /opt/sde