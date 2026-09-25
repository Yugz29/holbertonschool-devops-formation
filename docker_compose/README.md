# Docker Compose

## About

This project uses Docker Compose to describe and run multi-container
applications from a single `compose.yaml` file: a reverse proxy, an API
built from a Dockerfile and a database, started and stopped with one
command.

## Tasks

| Task | Description |
|---|---|
| [0-first_stack](./0-first_stack) | Run an `nginx` → Flask → Postgres stack with one `docker compose up`: only `nginx` is published on port `8080`, `/api` is proxied to the Flask app, and the Postgres password stays out of Git in a `.env` file. |
| [1-healthchecks](./1-healthchecks) | Add a `pg_isready` healthcheck to Postgres and make the API wait for `condition: service_healthy`, with real logs showing `db` healthy before `api` starts and a counter-example where a plain `depends_on` loses the race. |
| [2-full_stack](./2-full_stack) | Add a Redis cache with a `redis-cli ping` healthcheck: the API reads `/api` data with the cache-aside pattern (Redis first, Postgres on a miss, 30 s TTL) and reports `"cache": "hit"` or `"miss"`, while nginx stays the only published port. |
| [3-fix_stack](./3-fix_stack) | Fix a `compose.yaml` that will not start: a `depends_on` typo pointing to a missing service, two services publishing host port `8080`, and a Postgres container without `POSTGRES_PASSWORD`. |
