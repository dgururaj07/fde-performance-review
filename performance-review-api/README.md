# Performance Review API

FastAPI + PostgreSQL (psycopg 3, plain SQL). Contract: `employee-performance-review-openapi.json`.

## Layout

```
db/connection.py        connection helpers, loads .env
db/schema.sql           table definitions
models/                 Pydantic models
repositories/           SQL queries
services/services.py    business logic
main.py                 FastAPI app and routes
tests/                  pytest tests
```

## Setup

1. Install dependencies (from the repo root):
   ```
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```
2. Set the database connection in `.env`: `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`.
3. Create the tables if needed: `psql -f db/schema.sql`.
4. The `PGUSER` needs privileges on the tables (run as the table owner):
   ```sql
   GRANT SELECT, INSERT, DELETE ON employees, review_periods, performance_reviews TO fde_user;
   GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO fde_user;
   ```
   SELECT is enough to run the API; INSERT/DELETE and sequence usage are needed by the tests.

## Run

From `performance-review-api/`:

```
..\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

- Swagger UI: http://localhost:8000/docs
- `GET http://localhost:8000/api/reviews?employee_id=1&period_id=1` (both filters optional)
- `GET http://localhost:8000/api/reviews/101` (one review; 404 if it does not exist)

## Test

From `performance-review-api/`:

```
..\.venv\Scripts\python.exe -m pytest
```

The review tests insert their own employees, periods and reviews, and delete them afterwards.
