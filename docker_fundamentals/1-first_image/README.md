# First Docker Image

This task creates a small Flask web application and runs it inside a Docker container.

## Build the image

```bash
docker build -t first-image .
```

## Run the container

```bash
docker run --rm -p 5001:5000 first-image
```

The application listens on port `5000` inside the container.

Port `5001` is used on the host because port `5000` was already in use locally.

## Test the application

```bash
curl http://localhost:5001
```

Expected output:

```text
Hello from Docker!
```
