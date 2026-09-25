# Fix a Stack That Will Not Start

The provided `compose.yaml` (4 services: `db`, `cache`, `web`, `api`)
refused to come up for three separate reasons. Only `compose.yaml` was
changed, and the stack was not redesigned.

## The fixes

```diff
   db:
     image: postgres:16
-    # (le mot de passe de la base a disparu quelque part...)
+    environment:
+      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-changeme}
     healthcheck:
@@
   api:
     image: nginx:alpine
     ports:
-      - "8080:8080"
+      - "8081:80"
     depends_on:
-      - databse
+      - db
```

### 1. `api` depends on a service that does not exist

`depends_on` pointed to `databse`, a typo for `db`. Compose validates
the file before creating anything, so nothing starts:

```text
service "api" depends on undefined service "databse": invalid compose project
```

Fix: `depends_on: [db]`.

### 2. Two services publish the same host port

`web` and `api` both published host port `8080`. A host port can only be
bound once, so `api` stayed in `Created`:

```text
Error response from daemon: failed to set up container networking: driver failed programming external connectivity on endpoint fixstack-api-1 (…): Bind for 0.0.0.0:8080 failed: port is already allocated
```

Fix: publish `api` on host port `8081`. The container side is also
changed from `8080` to `80`, because `nginx:alpine` listens on port `80`
(`docker image inspect nginx:alpine` shows `{"80/tcp":{}}`). With `8080`,
the mapping would point to a port where nothing listens.

### 3. The database has no superuser password

The `postgres` image refuses to initialise a database without a
password, so `db` exited with code `1`:

```text
Error: Database is uninitialized and superuser password is not specified.
       You must specify POSTGRES_PASSWORD to a non-empty value for the
       superuser. For example, "-e POSTGRES_PASSWORD=password" on "docker run".
```

Fix: set `POSTGRES_PASSWORD`. The value is read from the environment or
from a `.env` file next to `compose.yaml` (ignored by Git). When neither
is set, it falls back to the placeholder `changeme`, so a fresh clone
still starts with a plain `docker compose up`.

```bash
echo "POSTGRES_PASSWORD=a-real-password" > .env
```

## Run the stack

```bash
docker compose up -d
docker compose ps
```

```text
NAME                  IMAGE            COMMAND                  SERVICE   CREATED         STATUS                   PORTS
3-fix_stack-api-1     nginx:alpine     "/docker-entrypoint.…"   api       8 seconds ago   Up 8 seconds             0.0.0.0:8081->80/tcp, [::]:8081->80/tcp
3-fix_stack-cache-1   redis:7-alpine   "docker-entrypoint.s…"   cache     8 seconds ago   Up 8 seconds             6379/tcp
3-fix_stack-db-1      postgres:16      "docker-entrypoint.s…"   db        8 seconds ago   Up 8 seconds (healthy)   5432/tcp
3-fix_stack-web-1     nginx:alpine     "/docker-entrypoint.…"   web       8 seconds ago   Up 8 seconds             0.0.0.0:8080->80/tcp, [::]:8080->80/tcp
```

After 37 seconds all four containers were still `running` with
`RestartCount` `0`.

## Test the stack

```bash
curl -I http://localhost:8080   # web
curl -I http://localhost:8081   # api
```

Both answer `HTTP/1.1 200 OK`.

The credentials work over the network, from another container on the
stack network:

```bash
docker run --rm --network 3-fix_stack_default -e PGPASSWORD=changeme \
  postgres:16 psql -h db -U postgres -tAc 'SELECT current_user'
```

```text
postgres
```

With a wrong password:

```text
psql: error: connection to server at "db" (172.18.0.2), port 5432 failed: FATAL:  password authentication failed for user "postgres"
```

## Stop the stack

```bash
docker compose down -v
```
