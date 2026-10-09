# 1 - Make containers talk

## Goal

Create a custom bridge network, run two containers on it, and have one reach the other **by container name**, not by IP.

## Commands and output

### 1. Create a custom bridge network

```bash
$ docker network create appnet
f3e36033f530e174104002ba7786fcaef107cf571684d07d39d7ac2eb3ed8338
```

### 2. Start a web server on that network

```bash
$ docker run -d --name web --network appnet nginx:alpine
dc8058a4a44a089f43d858922fea1a3892c512b1f5eadd3b5f9e39c08ddc28c4
```

### 3. Reach it by name with `ping`

```bash
$ docker run --rm --network appnet alpine ping -c 3 web
PING web (172.18.0.2): 56 data bytes
64 bytes from 172.18.0.2: seq=0 ttl=64 time=0.075 ms
64 bytes from 172.18.0.2: seq=1 ttl=64 time=0.176 ms
64 bytes from 172.18.0.2: seq=2 ttl=64 time=0.162 ms

--- web ping statistics ---
3 packets transmitted, 3 packets received, 0% packet loss
round-trip min/avg/max = 0.075/0.137/0.176 ms
```

The name `web` was resolved to `172.18.0.2` by Docker's embedded DNS. No IP was typed.

### 4. Reach it by name over HTTP with `curl`

```bash
$ docker run --rm --network appnet curlimages/curl -s http://web
<!DOCTYPE html>
<html>
<head>
<title>Welcome to nginx!</title>
...
```

The client container got the nginx welcome page from `http://web`.

### 5. Inspect the network

```bash
$ docker network inspect appnet
...
"Driver": "bridge",
...
"Subnet": "172.18.0.0/16",
"Gateway": "172.18.0.1"
...
"Containers": {
    "dc8058a4...": {
        "Name": "web",
        "IPv4Address": "172.18.0.2/16",
    }
}
```

`appnet` is a user-defined bridge network, with its own subnet, and `web` is attached to it.

## Counter-proof: the default bridge has no name resolution

```bash
$ docker run -d --name web2 nginx:alpine
46b16b90af3556665878236e908f574fccb03d3d9299d17dd080369ed980da34

$ docker run --rm alpine ping -c 2 web2
ping: bad address 'web2'
```

Without `--network`, containers land on the default `bridge` network, which has no embedded DNS: the name `web2` cannot be resolved.

## Why it matters

- On a **custom network**, Docker runs an embedded DNS server: every container is reachable by its name.
- Container IPs are assigned dynamically and change when a container is recreated, so hardcoding them breaks.
- Names are stable: an app can always connect to `db` or `web`, whatever IP the container gets.
- A custom network also isolates groups of containers: only containers on `appnet` can reach `web` this way.

## Cleanup

```bash
docker rm -f web web2
docker network rm appnet
```
