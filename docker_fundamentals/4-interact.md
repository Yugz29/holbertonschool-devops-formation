# Talk to your container

The task 1 image (`1-first_image`) now reads its message from the
`GREETING` environment variable. If `GREETING` is not set, the app falls
back to the original message, so task 1 behaves exactly as before.

```python
greeting = os.environ.get("GREETING", "Hello from Docker!")
```

Port `5001` is used on the host because port `5000` is taken by the
macOS AirPlay Receiver. The app still listens on `5000` inside the
container.

All outputs below are real. Colour codes were removed from the
`docker logs` output.

## Build the image

```bash
cd 1-first_image
docker build -t first-image .
```

```text
#10 naming to docker.io/library/first-image:latest done
#10 unpacking to docker.io/library/first-image:latest 0.1s done
#10 DONE 0.4s
```

(Output trimmed to the last lines.)

## Without `-e`: default message

```text
$ docker run -d --name talk-default -p 5001:5000 first-image
5e516cad5d40903f441a0c3cba4a3123abc5620619279242d6ae27b6bcd15d6a

$ curl -s http://localhost:5001
Hello from Docker!

$ docker exec talk-default printenv GREETING
```

`printenv` prints nothing and exits with code `1`: the variable does not
exist in the container.

```text
$ docker rm -f talk-default
talk-default
```

## 1. Pass the variable at run time (`-e`)

```text
$ docker run -d --name talk -p 5001:5000 -e GREETING="Hello from Holberton!" first-image
a44465b2ab95e64c40f0295d56bbb6f016547f6c47438d9c876f34e90c4a708f

$ docker ps --filter name=talk --format "{{.Names}}  {{.Status}}  {{.Ports}}"
talk  Up 3 seconds  0.0.0.0:5001->5000/tcp, [::]:5001->5000/tcp

$ curl -s http://localhost:5001
Hello from Holberton!
```

## 2. Read it from inside the container (`docker exec`)

```text
$ docker exec talk printenv GREETING
Hello from Holberton!

$ docker exec talk env
PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
HOSTNAME=a44465b2ab95
GREETING=Hello from Holberton!
LANG=C.UTF-8
GPG_KEY=7169605F62C751356D054A26A821E680E5FA6305
PYTHON_VERSION=3.12.14
PYTHON_SHA256=5c8462af5790baf43a321a1559dbe0db06d1be4300fb85fb53c40060668e548a
HOME=/root

$ docker exec talk sh -c 'export GREETING="Changed from exec"; printenv GREETING'
Changed from exec

$ curl -s http://localhost:5001
Hello from Holberton!
```

## 3. Inspect it from the host (`docker inspect`, `docker logs`)

```text
$ docker inspect --format '{{json .Config.Env}}' talk
["GREETING=Hello from Holberton!","PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin","LANG=C.UTF-8","GPG_KEY=7169605F62C751356D054A26A821E680E5FA6305","PYTHON_VERSION=3.12.14","PYTHON_SHA256=5c8462af5790baf43a321a1559dbe0db06d1be4300fb85fb53c40060668e548a"]

$ docker logs talk
 * Serving Flask app 'app'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://172.17.0.2:5000
Press CTRL+C to quit
192.168.65.1 - - [25/Sep/2026 15:25:09] "GET / HTTP/1.1" 200 -
192.168.65.1 - - [25/Sep/2026 15:25:10] "GET / HTTP/1.1" 200 -
```

## Cleanup

```text
$ docker rm -f talk
talk
```

## Observations

1. Without `-e`, `GREETING` does not exist inside the container at all
   (`printenv` exits with code `1`). The default message comes from the
   Python code, not from Docker. That is why task 1 still answers
   `Hello from Docker!` with the same `docker run` command as before.

2. The container's environment is the image's environment plus what I
   passed with `-e`. `PATH`, `LANG`, `GPG_KEY`, `PYTHON_VERSION` and
   `PYTHON_SHA256` come from the `python:3.12-slim` base image, and
   `GREETING` comes from my `docker run`. `env` inside the container also
   shows `HOSTNAME` (the short container ID) and `HOME`, which are not in
   `docker inspect`'s `Config.Env`: they are set when the process
   starts, not stored in the container config.

3. `docker exec` starts a new process in the running container. The
   `export` only changed the variable for that one `sh` process. The
   Flask process kept its own environment and still answered
   `Hello from Holberton!`. To change the value, the container has to be
   recreated with a new `-e`.

4. `docker inspect` shows every environment variable from the host
   without entering the container. Anyone who can run `docker inspect`
   can read them, so plain `-e` is not a safe place for secrets.

5. `docker logs` shows the main process's output: the Flask startup
   lines, then one line per `curl`. The two `GET /` lines match my two
   requests to this container. They come from `192.168.65.1`, not
   `127.0.0.1`: on Docker Desktop for Mac, traffic to the published port
   is forwarded through Docker's VM network before reaching the
   container.
