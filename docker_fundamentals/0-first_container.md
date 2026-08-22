# First container

## Commands used

\`\`\`bash
docker pull nginx
docker run -d -p 8080:80 --name my-nginx nginx
curl http://localhost:8080
docker exec -it my-nginx bash
ls /usr/share/nginx/html
cat /usr/share/nginx/html/index.html
ls /etc/nginx
cat /etc/nginx/nginx.conf
exit
docker logs my-nginx
docker stop my-nginx
docker rm my-nginx
\`\`\`

## Observations

1. The image and the running container are two different things: `nginx`
   is a frozen template pulled once from the registry, while `my-nginx`
   was a live instance created from it. I could stop and remove that
   instance without affecting the image itself — running `docker run`
   again would create a brand new container from the same image.

2. Inside the container, `/usr/share/nginx/html/index.html` was exactly
   the HTML page I got back from `curl`. Nginx isn't doing anything
   fancy by default, it's serving a static file straight off disk.

3. The logs showed : before nginx even starts, the
   container runs an entrypoint script that tunes the config (enabling
   IPv6, adjusting the number of worker processes based on available
   CPUs). So a container isn't just "the image running as-is", there's
   an initialization step first.
