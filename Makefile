amazon-data:
	python3 scripts/amazon_raw_sales_data.py

external-data:
	python3 scripts/external_invoices_reimbursements.py

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