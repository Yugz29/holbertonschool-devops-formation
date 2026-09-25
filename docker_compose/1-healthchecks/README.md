# Order Matters

This task starts from the [0-first_stack](../0-first_stack) stack
(`web` → `api` → `db`) and makes the start order reliable:

- `db` has a real healthcheck based on `pg_isready`.
- `api` waits for `db` to be **healthy**, not just started.
- `api` connects to Postgres when it starts and logs
  `Connected to database`. It exits with code `1` if the database is not
  reachable, and does not retry, so a wrong start order is easy to spot.

## The healthcheck

```yaml
  api:
    depends_on:
      db:
        condition: service_healthy

  db:
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -h localhost -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
      interval: 5s
      timeout: 5s
      retries: 5
      start_period: 10s
```

- `$$` escapes the `$` for Compose, so `POSTGRES_USER` and `POSTGRES_DB`
  are read from the environment inside the `db` container.
- `-h localhost` makes `pg_isready` connect over TCP. While the Postgres
  image initialises the database, it runs a temporary server that only
  listens on a Unix socket. Without `-h`, the check could pass during that
  phase, before the API is able to connect.

## Configure the password

```bash
cp .env.example .env
```

Then replace `change-me` with a real password in `.env`.

## Start the stack

```bash
docker compose up -d
```

Real output (excerpt): Compose waits for `db` to be `Healthy` before it
starts `api`.

```text
 Container 1-healthchecks-db-1 Starting
 Container 1-healthchecks-db-1 Started
 Container 1-healthchecks-db-1 Waiting
 Container 1-healthchecks-db-1 Healthy
 Container 1-healthchecks-api-1 Starting
 Container 1-healthchecks-api-1 Started
 Container 1-healthchecks-web-1 Starting
 Container 1-healthchecks-web-1 Started
```

## Check the status

While `db` is still being checked:

```bash
docker compose ps -a
```

```text
NAME                   IMAGE                COMMAND                  SERVICE   CREATED         STATUS                           PORTS
1-healthchecks-api-1   1-healthchecks-api   "python app.py"          api       2 seconds ago   Created
1-healthchecks-db-1    postgres:18-alpine   "docker-entrypoint.s…"   db        2 seconds ago   Up 1 second (health: starting)   5432/tcp
1-healthchecks-web-1   nginx:1.30-alpine    "/docker-entrypoint.…"   web       2 seconds ago   Created
```

Once the stack is up:

```bash
docker compose ps
```

```text
NAME                   IMAGE                COMMAND                  SERVICE   CREATED              STATUS                        PORTS
1-healthchecks-api-1   1-healthchecks-api   "python app.py"          api       About a minute ago   Up About a minute             5000/tcp
1-healthchecks-db-1    postgres:18-alpine   "docker-entrypoint.s…"   db        About a minute ago   Up About a minute (healthy)   5432/tcp
1-healthchecks-web-1   nginx:1.30-alpine    "/docker-entrypoint.…"   web       About a minute ago   Up About a minute             0.0.0.0:8080->80/tcp, [::]:8080->80/tcp
```

Only `db` shows a health status, because it is the only service with a
healthcheck.

## Proof of the order

Timeline of a real run (UTC), built from `docker events` and
`docker compose logs -t`:

| Time | Event |
|---|---|
| 15:48:13.304 | `db` container started |
| 15:48:14.005 | Postgres ready to accept TCP connections |
| 15:48:18.340 | `db` marked `healthy` (first check, one `interval` after start) |
| 15:48:18.881 | `api` container started |
| 15:48:19.114 | `api` logs `Connected to database` |

```bash
docker compose logs -t db api | grep -E 'init process complete|listening on IPv4|ready to accept|Connected' | sort -k3
```

```text
db-1   | 2026-09-25T15:48:13.757483042Z 2026-09-25 15:48:13.757 UTC [46] LOG:  database system is ready to accept connections
db-1   | 2026-09-25T15:48:13.985293043Z PostgreSQL init process complete; ready for start up.
db-1   | 2026-09-25T15:48:14.000018668Z 2026-09-25 15:48:13.999 UTC [1] LOG:  listening on IPv4 address "0.0.0.0", port 5432
db-1   | 2026-09-25T15:48:14.004951418Z 2026-09-25 15:48:14.004 UTC [1] LOG:  database system is ready to accept connections
api-1  | 2026-09-25T15:48:19.114312378Z INFO Connected to database: PostgreSQL 18.6 on aarch64-unknown-linux-musl, compiled by gcc (Alpine 15.2.0) 15.2.0, 64-bit
```

The first `ready to accept connections` comes from the temporary
initialisation server (Unix socket only). The real server listens on TCP
from `15:48:14.000`.

```bash
docker events --since 5m --until 0s --filter type=container \
  --filter label=com.docker.compose.project=1-healthchecks | grep -E ' (start|health_status)'
```

```text
2026-09-25T17:48:13.304544334+02:00 container start 169df59fa18f… (… name=1-healthchecks-db-1 …)
2026-09-25T17:48:18.340136003+02:00 container health_status: healthy 169df59fa18f… (… name=1-healthchecks-db-1 …)
2026-09-25T17:48:18.881186962+02:00 container start 9de764652e17… (… name=1-healthchecks-api-1 …)
2026-09-25T17:48:18.943330837+02:00 container start 1f731ba38ec8… (… name=1-healthchecks-web-1 …)
```

Container IDs and labels are shortened. `docker events` prints local
time (UTC+2 here).

## Counter-example: `depends_on` without a condition

The same stack was started from a temporary copy of `compose.yaml` where
only the `api` dependency changed:

```diff
     depends_on:
-      db:
-        condition: service_healthy
+      - db
```

```bash
docker compose -p race -f /tmp/compose.race.yaml --project-directory . up -d
docker compose -p race -f /tmp/compose.race.yaml --project-directory . ps -a
```

```text
NAME         IMAGE                COMMAND                  SERVICE   CREATED         STATUS                            PORTS
race-api-1   race-api             "python app.py"          api       4 seconds ago   Exited (1) 3 seconds ago
race-db-1    postgres:18-alpine   "docker-entrypoint.s…"   db        4 seconds ago   Up 4 seconds (health: starting)   5432/tcp
race-web-1   nginx:1.30-alpine    "/docker-entrypoint.…"   web       4 seconds ago   Up 4 seconds                      0.0.0.0:8080->80/tcp, [::]:8080->80/tcp
```

`api` started 48 ms after `db`, while Postgres was still initialising,
and lost the race:

```text
api-1  | 2026-09-25T15:50:13.543115167Z ERROR Cannot connect to database, exiting: connection failed: connection to server at "172.18.0.2", port 5432 failed: Connection refused
api-1  | 2026-09-25T15:50:13.543127959Z 	Is the server running on that host and accepting TCP/IP connections?
db-1   | 2026-09-25T15:50:14.010936418Z PostgreSQL init process complete; ready for start up.
db-1   | 2026-09-25T15:50:14.025446793Z 2026-09-25 15:50:14.025 UTC [1] LOG:  listening on IPv4 address "0.0.0.0", port 5432
db-1   | 2026-09-25T15:50:14.029848251Z 2026-09-25 15:50:14.029 UTC [1] LOG:  database system is ready to accept connections
```

A plain `depends_on` only waits for the `db` container to be **started**.
Postgres opened its TCP port about 0.5 s after the API tried to connect.
The API stays down after that, so `curl http://localhost:8080/api`
returns `502 Bad Gateway`.

## Test the stack

```bash
curl http://localhost:8080
curl http://localhost:8080/api
```

Expected output for `/api`:

```json
{"db_version":"PostgreSQL 18.6 on aarch64-unknown-linux-musl, compiled by gcc (Alpine 15.2.0) 15.2.0, 64-bit","message":"Hello from the API!"}
```

## Stop the stack

```bash
docker compose down -v
```

`-v` also removes the anonymous volume created by the Postgres image.
