## Intro.

This repository contains a database application containing business e-commerce data. The
application consists of a PostgreSQL database hosting all data, a data ingestor/loader
which loads the data into the DB and a [Metabase](https://www.metabase.com/) dashboard to
view the data in Postgres.


## How to run it?

Pre-requisites:

- Linux or MacOS
- Docker
- Web browser

1. Clone this git repo.
```
git clone https://github.com/saleemayman/carpet_invoices.git
```

2. `cd` into the cloned repo: `cd carpet_invoices`.

3. Consolidate country wise AMZ sales data into a single and formatted CSV file using:
```
make amazon-data
```

4. Consolidate all monthly external invoices into a single CSV and parse the corresponding invoice and reimbursement PDFs for items the invoice/reimbursement was issued for using:
```
make external-data
```

5. From root (`carpet_invoices`) run: `make ingestor` to start the DB and load data into it.
This will first create the `postgres` database service and once its ready, the `ingestor` service will load data into it and terminate.

6. To start the Metabase dashboard, run: `make dashboard`. Once the service starts running,
check it in a web browser at: `localhost:3000`.
