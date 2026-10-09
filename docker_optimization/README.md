# Docker Optimization

From "it builds" to "I'd run this in production": persistence, networking, image size, build speed and security, all measured.

## Tasks

| Task | Topic | Deliverable |
|---|---|---|
| 0 | Persist data with a named volume | [`0-persistence.md`](0-persistence.md) |
| 1 | Container name resolution on a custom network | [`1-networking.md`](1-networking.md) |
| 2 | Shrink a bloated Node image | [`2-optimize/`](2-optimize/) |
| 3 | Fix a broken multi-stage Go build | [`3-multistage/`](3-multistage/) |
| 4 | Harden an Express image (non-root + healthcheck) | [`4-harden/`](4-harden/) |

---

## 2 - Shrink it

### Baseline (original Dockerfile)

```dockerfile
FROM node:20
WORKDIR /app
COPY . .
RUN npm install
CMD ["node", "index.js"]
```

Problems:

- `node:20` is a full Debian image with build tools the app never uses.
- `COPY . .` runs before `npm install`: any code change invalidates the cache, so dependencies are reinstalled on every build.
- No `.dockerignore`: the whole folder (local `node_modules`, `.git`, ...) is sent to the build.
- No `USER`: the app runs as root.

### Optimized Dockerfile

```dockerfile
FROM node:20-alpine

ENV NODE_ENV=production
WORKDIR /app

COPY package*.json ./
RUN npm install --omit=dev && npm cache clean --force

COPY index.js ./

USER node
EXPOSE 3000
CMD ["node", "index.js"]
```

Changes:

1. **Lighter base**: `node:20-alpine` instead of `node:20`.
2. **Layer ordering**: `package*.json` is copied and installed before the source code, so the dependency layer stays cached when only code changes.
3. **Production deps only**: `--omit=dev` and `npm cache clean --force` keep dev dependencies and the npm cache out of the image.
4. **`.dockerignore`**: excludes `node_modules`, `.git`, `.env`, logs and docs from the build context.
5. **Non-root**: runs as the built-in `node` user. Source files stay owned by root, so the app can read them but not modify them.

### Measurement method

- Size: `docker images <tag>` (DISK USAGE column).
- Rebuild time: `time docker build -t <tag> .` after adding a comment to `index.js`.

### Before / after

| Metric | Before (`node:20`) | After (`node:20-alpine`) | Change |
|---|---|---|---|
| Image size (disk usage) | 1.58 GB | 199 MB | **-87%** |
| Image size (content size) | 392 MB | 49.7 MB | -87% |
| Rebuild after a code-only change | 2.56 s | 0.56 s | **~4.5x faster** |
| `npm install` on code-only change | re-run (1.3 s) | `CACHED` | dependencies from cache |
| Runtime user | root | `node` | non-root |

Rebuild output after a code-only change (optimized image):

```
=> CACHED [2/5] WORKDIR /app
=> CACHED [3/5] COPY package*.json ./
=> CACHED [4/5] RUN npm install --omit=dev && npm cache clean --force
=> [5/5] COPY index.js ./
```

### Run check

```bash
$ docker run -d -p 3000:3000 --name opt app:after
$ curl localhost:3000
Optimize me!
$ docker exec opt whoami
node
```

---

## 3 - One image to build, another to ship

A small Go server (port 8080) with a broken multi-stage build. Only the `Dockerfile` was modified; the Go code is untouched.

### Original Dockerfile

```dockerfile
FROM golang:1.22 AS builder
WORKDIR /src
COPY . .
RUN go build -o /app/server .

FROM alpine:3.20
COPY --from=build /app/server /server
CMD ["/server"]
```

### Bugs found

1. **Wrong stage name**: the first stage is named `builder`, but the final stage copies `--from=build`. No stage has that name, so Docker tries to pull an image called `build` from Docker Hub:
   ```
   failed to resolve source metadata for docker.io/library/build:latest: pull access denied
   ```
2. **Dynamic linking (hidden bug)**: `golang:1.22` is Debian-based (glibc), while `alpine` uses musl. With CGO enabled (the default), a binary using `net` may be linked against glibc and fail to start on Alpine with a misleading `not found` error. `CGO_ENABLED=0` produces a fully static binary.

### Fixed Dockerfile

```dockerfile
FROM golang:1.22 AS builder

WORKDIR /src
COPY go.mod ./
COPY *.go ./
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o /app/server .

FROM alpine:3.20
COPY --from=builder /app/server /server
USER nobody
EXPOSE 8080
CMD ["/server"]
```

Changes:

1. `--from=builder` matches the stage name.
2. `CGO_ENABLED=0` builds a static binary that runs on Alpine.
3. `-ldflags="-s -w"` strips debug symbols for a smaller binary.
4. Only `go.mod` and `*.go` are copied, not the whole folder.
5. `USER nobody`: the server runs as non-root.

### Results

| Image | Disk usage | Content size |
|---|---|---|
| Build stage (`--target builder`, Go toolchain) | 1.3 GB | 306 MB |
| Final image (`alpine` + binary) | **20.1 MB** | 6.03 MB |

The final image is about **98% smaller** than the build stage.

### Run check

```bash
$ docker run -d -p 8080:8080 --name gosrv multi:fixed
$ curl localhost:8080
Hello from Go in Docker!
$ docker exec gosrv whoami
nobody
$ docker exec gosrv sh -c "which go || echo 'no go toolchain'"
no go toolchain
```

---

## 4 - Harden it

An Express app (port 3000, `/health` endpoint) with a broken non-root setup and healthcheck. Only the `Dockerfile` was modified.

### Original Dockerfile

```dockerfile
FROM node:20-alpine
WORKDIR /usr/src/app
RUN addgroup app && adduser -S -G app app
USER app
COPY package*.json ./
RUN npm install
COPY . .
HEALTHCHECK CMD curl -f http://localhost:8080/health || exit 1
CMD ["node", "server.js"]
```

### Bugs found

1. **Permission error at build time**: `WORKDIR` creates `/usr/src/app` as root, then `USER app` switches to a user that cannot write there, so `npm install` fails:
   ```
   npm error Error: EACCES: permission denied, mkdir '/usr/src/app/node_modules'
   ```
2. **Wrong port**: the healthcheck targets `8080`, but the app listens on `3000`.
3. **Missing tool**: `curl` is not installed in `node:20-alpine`. BusyBox `wget` is available in every Alpine image.

### Fixed Dockerfile

```dockerfile
FROM node:20-alpine

ENV NODE_ENV=production
WORKDIR /usr/src/app

RUN addgroup -S app && adduser -S -G app app

COPY package*.json ./
RUN npm install --omit=dev && npm cache clean --force
COPY server.js ./

USER app
EXPOSE 3000

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -q --spider http://localhost:3000/health || exit 1

CMD ["node", "server.js"]
```

Changes:

1. Dependencies are installed as root, and `USER app` is set **after** the build steps. Files stay owned by root: the app can read them but cannot modify its own code.
2. The healthcheck targets port `3000`.
3. `wget -q --spider` replaces `curl`: it only checks that the URL answers, without downloading the page.
4. Healthcheck timing (`--interval=10s --start-period=5s`) so the container reports healthy quickly instead of waiting for the 30 s default.
5. Only `server.js` is copied, production dependencies only.

### Run check

```bash
$ docker run -d -p 3000:3000 --name hardened harden:fixed
$ docker exec hardened whoami
app
$ docker exec hardened sh -c "which curl || echo 'no curl'; which wget"
no curl
/usr/bin/wget
$ docker ps --filter name=hardened
CONTAINER ID   IMAGE          STATUS                    PORTS                    NAMES
bb681740faad   harden:fixed   Up 15 seconds (healthy)   0.0.0.0:3000->3000/tcp   hardened
$ docker inspect --format '{{json .State.Health}}' hardened
{"Status":"healthy","FailingStreak":0,"Log":[{"ExitCode":0,...},{"ExitCode":0,...}]}
```

---

## Why scan images

An image ships an OS and libraries, each of which can contain known vulnerabilities (CVEs). A scanner like Trivy (`trivy image <name>`) compares the image's packages against vulnerability databases. Smaller images (alpine, distroless, multi-stage) contain fewer packages, so they expose fewer vulnerabilities to begin with.
