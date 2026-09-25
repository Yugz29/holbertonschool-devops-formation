# Grow the Stack

This task starts from the [1-healthchecks](../1-healthchecks) stack and
adds a Redis cache in front of Postgres.

| Service | Image | Role |
|---|---|---|
| `web` | `nginx:1.30-alpine` | Reverse proxy, the only published port (`8080`). Proxies `/api` to the `api` service. |
| `api` | built from [`api/Dockerfile`](./api/Dockerfile) | Flask app. Reads the Postgres version through a Redis cache. |
| `db` | `postgres:18-alpine` | PostgreSQL database with a `pg_isready` healthcheck. |
| `redis` | `redis:8-alpine` | Cache with a `redis-cli ping` healthcheck. |

```text
client ──► web (nginx, :8080) ──/api──► api (Flask, :5000) ──► redis:6379  (cache)
                                                           └──► db:5432     (Postgres)
```

- Only `web` publishes a port. `api`, `db` and `redis` are only reachable
  on the Compose network, by their service names.
- `api` waits for both `db` and `redis` to be healthy
  (`condition: service_healthy`). At startup it checks both connections,
  logs `Connected to database` and `Connected to Redis`, and exits if one
  of them fails.

## Cache-aside on `/api`

On each `GET /api`, the API:

1. Reads the `db_version` key from Redis.
2. If the key exists, it returns the cached value with `"cache": "hit"`.
3. If the key is missing, it runs `SELECT version()` on Postgres, stores
   the result in Redis with a TTL of 30 seconds (`CACHE_TTL`) and returns
   it with `"cache": "miss"`.

After 30 seconds Redis deletes the key, so the next request is a miss
again and reads a fresh value from Postgres.

If Redis is down, the API reads Postgres directly and answers with
`"cache": "bypass"` instead of failing: the cache speeds things up, but
the API does not depend on it to answer.

## The reverse proxy

[`nginx/default.conf`](./nginx/default.conf) serves the nginx welcome
page on `/` and forwards `/api` to `http://api:5000`. It also passes the
original request details to the API:

| Header | Value |
|---|---|
| `Host` | Host name asked by the client, without the port (`localhost`) |
| `X-Real-IP` | Client IP address |
| `X-Forwarded-For` | Chain of client and proxy IP addresses |
| `X-Forwarded-Proto` | Original scheme (`http`) |

The TCP connection always comes from nginx: Flask logs every request as
coming from `172.18.0.5`, the IP of the `web` container. These headers
are how the real client details reach the API. This app does not read
them yet; Flask would need the `ProxyFix` middleware to use them.

## Configure the password

```bash
cp .env.example .env
```

Then replace `change-me` with a real password in `.env`.

## Start the stack

```bash
docker compose up -d
```

The first run also pulls `redis:8-alpine` and builds the `api` image.
Real output (excerpt):

```text
 Container 2-full_stack-db-1 Starting
 Container 2-full_stack-redis-1 Starting
 Container 2-full_stack-db-1 Started
 Container 2-full_stack-redis-1 Started
 Container 2-full_stack-db-1 Waiting
 Container 2-full_stack-redis-1 Waiting
 Container 2-full_stack-redis-1 Healthy
 Container 2-full_stack-db-1 Healthy
 Container 2-full_stack-api-1 Starting
 Container 2-full_stack-api-1 Started
 Container 2-full_stack-web-1 Starting
 Container 2-full_stack-web-1 Started
```

```bash
docker compose ps
```

```text
NAME                   IMAGE                COMMAND                  SERVICE   CREATED         STATUS                   PORTS
2-full_stack-api-1     2-full_stack-api     "python app.py"          api       6 seconds ago   Up Less than a second    5000/tcp
2-full_stack-db-1      postgres:18-alpine   "docker-entrypoint.s…"   db        6 seconds ago   Up 5 seconds (healthy)   5432/tcp
2-full_stack-redis-1   redis:8-alpine       "docker-entrypoint.s…"   redis     6 seconds ago   Up 5 seconds (healthy)   6379/tcp
2-full_stack-web-1     nginx:1.30-alpine    "/docker-entrypoint.…"   web       6 seconds ago   Up Less than a second    0.0.0.0:8080->80/tcp, [::]:8080->80/tcp
```

Only `web` has a host mapping (`0.0.0.0:8080->80/tcp`). The other ports
(`5000/tcp`, `5432/tcp`, `6379/tcp`) are only open inside the Compose
network.

## Test the cache

Two requests in a row: the first one is a miss, the second one a hit.

```bash
curl http://localhost:8080/api
curl http://localhost:8080/api
```

```json
{"cache":"miss","db_version":"PostgreSQL 18.6 on aarch64-unknown-linux-musl, compiled by gcc (Alpine 15.2.0) 15.2.0, 64-bit","message":"Hello from the API!"}
{"cache":"hit","db_version":"PostgreSQL 18.6 on aarch64-unknown-linux-musl, compiled by gcc (Alpine 15.2.0) 15.2.0, 64-bit","message":"Hello from the API!"}
```

The key stored in Redis and its remaining lifetime in seconds:

```bash
docker compose exec redis redis-cli KEYS '*'
docker compose exec redis redis-cli TTL db_version
docker compose exec redis redis-cli GET db_version
```

```text
db_version
30
PostgreSQL 18.6 on aarch64-unknown-linux-musl, compiled by gcc (Alpine 15.2.0) 15.2.0, 64-bit
```

`KEYS '*'` is fine on this small demo database. On a large production
Redis, use `SCAN` instead, because `KEYS` blocks the server while it runs.

## Wait for the TTL to expire

```bash
while :; do
  t=$(docker compose exec -T redis redis-cli TTL db_version)
  echo "$(date +%T) TTL db_version = $t"
  [ "$t" = "-2" ] && break
  sleep 5
done
```

```text
17:59:19 TTL db_version = 20
17:59:24 TTL db_version = 15
17:59:30 TTL db_version = 10
17:59:35 TTL db_version = 4
17:59:40 TTL db_version = -2
```

`-2` means the key no longer exists. `-T` turns off the TTY so the output
can be stored in a variable. Once the key has expired, `KEYS '*'` returns
nothing and the next request is a miss again:

```bash
curl http://localhost:8080/api
```

```json
{"cache":"miss","db_version":"PostgreSQL 18.6 on aarch64-unknown-linux-musl, compiled by gcc (Alpine 15.2.0) 15.2.0, 64-bit","message":"Hello from the API!"}
```

The API logs show the same sequence:

```bash
docker compose logs api | grep -E 'Cache|GET /api'
```

```text
api-1  | INFO Cache miss for db_version, stored for 30s
api-1  | INFO 172.18.0.5 - - [25/Sep/2026 15:59:09] "GET /api HTTP/1.1" 200 -
api-1  | INFO Cache hit for db_version
api-1  | INFO 172.18.0.5 - - [25/Sep/2026 15:59:09] "GET /api HTTP/1.1" 200 -
api-1  | INFO Cache miss for db_version, stored for 30s
api-1  | INFO 172.18.0.5 - - [25/Sep/2026 15:59:40] "GET /api HTTP/1.1" 200 -
```

## When Redis is down

```bash
docker compose stop redis
curl http://localhost:8080/api
```

```json
{"cache":"bypass","db_version":"PostgreSQL 18.6 on aarch64-unknown-linux-musl, compiled by gcc (Alpine 15.2.0) 15.2.0, 64-bit","message":"Hello from the API!"}
```

```text
api-1  | WARNING Redis unavailable, skipping the cache: Error -2 connecting to redis:6379. Name or service not known.
```

After `docker compose start redis`, the next request is a miss and the
one after it a hit.

## Stop the stack

```bash
docker compose down -v
```

`-v` also removes the anonymous volume created by the Postgres image.
Redis has no volume: its data lives in the container and is removed with
it.
