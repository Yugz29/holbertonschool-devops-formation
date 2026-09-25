# Your First Stack

This task runs a three-service stack with a single `compose.yaml`:

| Service | Image | Role |
|---|---|---|
| `web` | `nginx:1.30-alpine` | Entry point on port `8080`. Serves the nginx welcome page and proxies `/api` to the `api` service. |
| `api` | built from [`api/Dockerfile`](./api/Dockerfile) | Flask app that connects to Postgres and returns a message plus the result of `SELECT version()`. |
| `db` | `postgres:18-alpine` | PostgreSQL database, only reachable from inside the stack. |

Only `web` publishes a port. `api` and `db` talk to each other on the
default Compose network, using the service names as host names.

## Configure the password

The Postgres password is read from a `.env` file that is not committed:

```bash
cp .env.example .env
```

Then replace `change-me` with a real password in `.env`.

## Start the stack

```bash
docker compose up
```

Add `-d` to run it in the background. Add `--build` to rebuild the `api`
image after changing its code.

Check that the three containers are up:

```bash
docker compose ps
```

## Test the stack

```bash
curl http://localhost:8080
```

Expected output: the HTML of the `Welcome to nginx!` page.

```bash
curl http://localhost:8080/api
```

Expected output:

```json
{"db_version":"PostgreSQL 18.6 on aarch64-unknown-linux-musl, compiled by gcc (Alpine 15.2.0) 15.2.0, 64-bit","message":"Hello from the API!"}
```

The exact version string depends on the image and the host architecture.

If Postgres is not ready yet, the API retries 3 times, then answers with
HTTP `503` instead of crashing:

```json
{"error":"Database is not ready yet, try again in a few seconds.","message":"Hello from the API!"}
```

Right after `docker compose up -d`, nginx can also answer `502 Bad Gateway`
for a second, while Flask is still starting.

## Stop the stack

```bash
docker compose down -v
```

`down` removes the containers and the network. `-v` also removes the
anonymous volume created by the Postgres image, so the database starts
empty next time.
