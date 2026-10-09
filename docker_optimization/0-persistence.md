# 0 - Persist your data

## Goal

Prove that data written by a stateful container (PostgreSQL) survives removing and recreating the container, using a **named volume**.

## Commands and output

### 1. Create a named volume

```bash
$ docker volume create pgdata
pgdata
```

### 2. Start a first container using the volume

```bash
$ docker run -d --name pg1 -e POSTGRES_PASSWORD=secret \
  -v pgdata:/var/lib/postgresql/data postgres:16
d3e06c9c65433a52420b918c7f6c1c3e1bad6fc1c7bae81ae079266f842028a6
```

`-v pgdata:/var/lib/postgresql/data` mounts the named volume on PostgreSQL's data directory.
The image is pinned to `postgres:16`: starting with version 18 the data path changed, so an unpinned `latest` would not write to this mount point.

### 3. Write some data

```bash
$ docker exec pg1 psql -U postgres -c "CREATE TABLE notes (id SERIAL PRIMARY KEY, msg TEXT); INSERT INTO notes (msg) VALUES ('hello from pg1');"
CREATE TABLE
INSERT 0 1
```

### 4. Remove the container

```bash
$ docker rm -f pg1
pg1
```

### 5. Recreate a new container on the same volume

```bash
$ docker run -d --name pg2 -e POSTGRES_PASSWORD=secret \
  -v pgdata:/var/lib/postgresql/data postgres:16
4f7942db648e428703f19e9342aeb380874c83eb28b0278152314c1cebad8016
```

### 6. Check the data

```bash
$ docker exec pg2 psql -U postgres -c "SELECT * FROM notes;"
 id |      msg
----+----------------
  1 | hello from pg1
(1 row)
```

## Observation

The row inserted from `pg1` is still there in `pg2`, a brand-new container.
The data lived in the `pgdata` volume, not in the container's writable layer, so deleting the container did not delete it.

## Named volume vs bind mount

| | Named volume | Bind mount |
|---|---|---|
| Syntax | `-v pgdata:/path` | `-v /host/path:/path` |
| Managed by | Docker (stored in Docker's storage area) | You (any folder on the host) |
| Portability | Same on every machine | Depends on the host's folder layout |
| Typical use | Database and app data | Source code during development |

A named volume is the right choice for database data: Docker manages its location and permissions, and it does not depend on the host's directory structure.

## Cleanup

```bash
docker rm -f pg2
docker volume rm pgdata
```
