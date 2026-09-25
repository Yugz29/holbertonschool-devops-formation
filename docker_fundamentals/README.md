# Docker Fundamentals

## About

This project introduces Docker through hands-on tasks: running and
exploring an existing container, building a first image from a
Dockerfile, then debugging a broken Dockerfile until the application
builds, starts and answers requests.

## Tasks

| Task | Description |
|---|---|
| [0-first_container.md](./0-first_container.md) | Run an `nginx` container, explore it with `docker exec` and `docker logs`, and note the difference between an image and a container. |
| [1-first_image](./1-first_image) | Write a Dockerfile for a small Flask app, build the image and run it as a container. |
| [2-fix_flask](./2-fix_flask) | Fix a broken Dockerfile for a Flask app so it builds, stays up and returns `Hello from Flask in Docker!` on port `5000`. |
| [3-fix_express](./3-fix_express) | Fix a broken Dockerfile for an Express app so it builds, stays up and returns `Hello from Express in Docker!` on port `3000`. |
